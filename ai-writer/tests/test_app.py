"""Integration tests for Flask application routes and API endpoints."""
import os
import tempfile
import pytest

# Point to temporary SQLite DB for test isolation
os.environ["HISTORY_DB"] = os.path.join(tempfile.gettempdir(), "test_ai_writer_history.db")

from app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            # Reset test db table
            db().execute("DROP TABLE IF EXISTS history")
            db().commit()
        yield client


def test_index_route(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"AI Writer" in res.data
    assert b"Summarize" in res.data


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert "models" in data


def test_api_models(client):
    res = client.get("/api/models")
    assert res.status_code == 200
    data = res.get_json()
    assert "distilbart" in data["models"]
    assert "metadata" in data


def test_api_sample(client):
    res = client.get("/api/sample")
    assert res.status_code == 200
    data = res.get_json()
    assert "text" in data
    assert len(data["text"]) > 50


def test_api_summarize_validation_too_short(client):
    res = client.post("/api/summarize", json={"text": "A brief note."})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_api_summarize_success_with_history(client):
    sample_text = (
        "Artificial intelligence and deep learning frameworks are rapidly reshaping modern software systems. "
        "Engineers and researchers deploy transformer architectures across search engines, coding assistants, "
        "and medical diagnostic platforms. By fine-tuning large pre-trained neural models on domain-specific corpora, "
        "organizations can automate complex knowledge retrieval workflows and achieve unprecedented productivity gains. "
        "Future developments will focus on reducing computational footprints, enhancing interpretability, "
        "and mitigating algorithmic biases in deployed consumer applications."
    )
    res = client.post(
        "/api/summarize",
        json={
            "text": sample_text,
            "model": "distilbart",
            "length": "medium",
            "format": "bullets",
            "save": True,
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "summary" in data
    assert "stats" in data
    assert data["stats"]["reduction_pct"] > 0
    entry_id = data["id"]
    assert entry_id is not None

    # Verify history retrieval
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    history = hist_res.get_json()
    assert len(history) == 1
    assert history[0]["id"] == entry_id

    # Verify single deletion
    del_res = client.delete(f"/api/history/{entry_id}")
    assert del_res.status_code == 204

    # Verify empty history
    hist_res2 = client.get("/api/history")
    assert len(hist_res2.get_json()) == 0


def test_api_history_clear(client):
    client.delete("/api/history")
    res = client.get("/api/history")
    assert len(res.get_json()) == 0
