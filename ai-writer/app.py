"""AI Writer with Text Summarization - Flask app."""
import html
import json
import os
import re
import sqlite3
import urllib.request
from datetime import datetime, timezone

from flask import Flask, g, jsonify, render_template, request

from readability import readability
import summarizer

DB_PATH = os.environ.get("HISTORY_DB", os.path.join(os.path.dirname(__file__), "history.db"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB request cap


# ---------- history (stored in SQLite) ----------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute(
            """CREATE TABLE IF NOT EXISTS history (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 created_at TEXT NOT NULL,
                 model TEXT NOT NULL,
                 format TEXT DEFAULT 'paragraph',
                 original TEXT NOT NULL,
                 summary TEXT NOT NULL,
                 stats TEXT NOT NULL)"""
        )
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


# ---------- routes ----------
@app.get("/")
def index():
    return render_template(
        "index.html",
        models=list(summarizer.MODELS),
        default_model=summarizer.DEFAULT_MODEL,
        model_metadata=summarizer.MODEL_METADATA,
        formats=summarizer.FORMATS,
    )


@app.get("/api/health")
def api_health():
    """Health check endpoint for container deployments & monitoring."""
    return jsonify(
        status="ok",
        models=list(summarizer.MODELS.keys()),
        default_model=summarizer.DEFAULT_MODEL,
    )


@app.get("/api/models")
def api_models():
    """Return model list and descriptive metadata."""
    return jsonify(
        models=summarizer.MODELS,
        metadata=summarizer.MODEL_METADATA,
        default=summarizer.DEFAULT_MODEL,
    )


@app.get("/api/sample")
def api_sample():
    """Load sample article for quick one-click testing."""
    sample_path = os.path.join(os.path.dirname(__file__), "samples", "sample_article.txt")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            return jsonify(text=f.read())
    return jsonify(text="Artificial Intelligence continues to transform modern software development...")


@app.post("/api/extract-url")
def api_extract_url():
    """Extract article body text from a provided web URL."""
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return jsonify(error="Please provide a valid HTTP or HTTPS URL."), 400

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36 AI-Writer/1.0"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "text/plain" not in content_type:
                return jsonify(error=f"Unsupported content type: {content_type}"), 400
            raw_html = response.read().decode("utf-8", errors="replace")

        # Basic HTML extraction: strip scripts, styles, and markup tags
        text = re.sub(r"<(script|style|nav|header|footer|aside)[^>]*>.*?</\1>", " ", raw_html, flags=re.DOTALL | re.IGNORECASE)
        # Strip remaining tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Decode entities and collapse whitespace
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()

        if len(text.split()) < 30:
            return jsonify(error="Could not extract enough readable text from the provided URL."), 400

        return jsonify(text=text)
    except Exception as e:
        return jsonify(error=f"Failed to fetch article from URL: {e}"), 400


@app.post("/api/summarize")
def api_summarize():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    model = data.get("model", summarizer.DEFAULT_MODEL)
    length = data.get("length", "medium")
    fmt = data.get("format", "paragraph")
    save = bool(data.get("save", True))

    try:
        result = summarizer.summarize(text, model=model, length=length, fmt=fmt)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        app.logger.exception("Summarization failed")
        return jsonify(error=f"The model could not run: {e}"), 500

    orig_stats = readability(text)
    sum_stats = readability(result["summary"])

    stats = {
        "original": orig_stats,
        "summary": sum_stats,
        "reduction_pct": round(
            100 * (1 - sum_stats["words"] / max(1, orig_stats["words"])), 1
        ),
        "chunks": result["chunks"],
        "format": result.get("format", fmt),
        "fallback": result.get("fallback", False),
    }

    entry_id = None
    if save:
        cur = db().execute(
            "INSERT INTO history (created_at, model, format, original, summary, stats) VALUES (?,?,?,?,?,?)",
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                result["model"],
                fmt,
                text,
                result["summary"],
                json.dumps(stats),
            ),
        )
        db().commit()
        entry_id = cur.lastrowid

    return jsonify(
        id=entry_id,
        summary=result["summary"],
        model=result["model"],
        stats=stats,
        format=fmt,
        fallback=result.get("fallback", False),
    )


@app.get("/api/history")
def api_history():
    rows = db().execute("SELECT * FROM history ORDER BY id DESC LIMIT 50").fetchall()
    results = []
    for r in rows:
        try:
            st = json.loads(r["stats"])
        except Exception:
            st = {}
        results.append({
            "id": r["id"],
            "created_at": r["created_at"],
            "model": r["model"],
            "format": r["format"] if "format" in r.keys() else "paragraph",
            "original": r["original"],
            "summary": r["summary"],
            "stats": st,
        })
    return jsonify(results)


@app.delete("/api/history/<int:entry_id>")
def api_history_delete(entry_id):
    db().execute("DELETE FROM history WHERE id = ?", (entry_id,))
    db().commit()
    return "", 204


@app.delete("/api/history")
def api_history_clear():
    db().execute("DELETE FROM history")
    db().commit()
    return "", 204


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f">> AI Writer is running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
