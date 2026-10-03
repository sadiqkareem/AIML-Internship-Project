"""Summarization engine: DistilBART / BART / T5 via Hugging Face, with long-article chunking and fallback."""
import os
import re
import threading
from collections import Counter

from readability import count_words

MODELS = {
    "distilbart": "sshleifer/distilbart-cnn-12-6",
    "bart": "facebook/bart-large-cnn",
    "t5": "t5-base",
    "t5-small": "t5-small",
}

MODEL_METADATA = {
    "distilbart": {
        "name": "DistilBART",
        "description": "Fast & efficient (~300MB, recommended for CPU/quick results)",
        "badge": "Fast",
    },
    "bart": {
        "name": "BART Large",
        "description": "High-accuracy CNN model (~1.6GB, best abstractive depth)",
        "badge": "Deep",
    },
    "t5": {
        "name": "T5 Base",
        "description": "Abstractive T5 model (~890MB, balanced style)",
        "badge": "Balanced",
    },
    "t5-small": {
        "name": "T5 Small",
        "description": "Ultra lightweight (~240MB, rapid)",
        "badge": "Compact",
    },
}

DEFAULT_MODEL = os.environ.get("SUMMARIZER_MODEL", "distilbart")

# Fraction of the source to keep, per length setting.
LENGTH_RATIOS = {"short": 0.15, "medium": 0.30, "long": 0.45}

FORMATS = ["paragraph", "bullets", "tldr"]

# Stay well under model token limits (~1024 tokens ~ 700 words)
CHUNK_WORDS = 450
MIN_WORDS = 35
MAX_WORDS = 30000

_pipes = {}
_lock = threading.Lock()

# Common abbreviations to avoid false sentence splits
_ABBREVIATIONS = (
    r"\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr)\.(?=\s+[A-Z])|"
    r"\b(?:e\.g|i\.e|vs|etc)\.(?=\s+[a-z0-9])|"
    r"\b(?:U\.S)\.(?=\s+[A-Za-z0-9])"
)



def _get_device() -> int:
    """Check if CUDA is available for GPU acceleration."""
    try:
        import torch
        if torch.cuda.is_available():
            return 0
    except Exception:
        pass
    return -1


def _get_pipe(model_key: str):
    """Load each model once and reuse it across requests."""
    with _lock:
        if model_key not in _pipes:
            from transformers import pipeline  # imported lazily
            device = _get_device()
            _pipes[model_key] = pipeline(
                "summarization",
                model=MODELS[model_key],
                device=device,
            )
        return _pipes[model_key]


def split_sentences(text: str) -> list[str]:
    """Split text into sentences while respecting common abbreviations."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    # Protect common abbreviations with non-breaking placeholder
    def _protect(match):
        return match.group(0).replace(".", "__DOT__")

    protected = re.sub(_ABBREVIATIONS, _protect, text, flags=re.IGNORECASE)
    parts = [s for s in re.split(r"(?<=[.!?])\s+", protected) if s]
    sentences = [s.replace("__DOT__", ".").strip() for s in parts if s.strip()]
    return sentences or [text]


def chunk_text(text: str, max_words: int = CHUNK_WORDS) -> list[str]:
    """Group whole sentences into chunks of at most `max_words` words."""
    chunks, current, size = [], [], 0
    for sent in split_sentences(text):
        words = sent.split()
        pieces = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)] or [sent]
        for piece in pieces:
            n = len(piece.split())
            if current and size + n > max_words:
                chunks.append(" ".join(current))
                current, size = [], 0
            current.append(piece)
            size += n
    if current:
        chunks.append(" ".join(current))
    return chunks


def _extractive_summarize(text: str, target_sentences: int = 3) -> str:
    """Pure-Python frequency-based sentence ranking fallback.
    Used when PyTorch/Transformers models cannot run or during offline fallback.
    """
    sentences = split_sentences(text)
    if len(sentences) <= target_sentences:
        return " ".join(sentences)

    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    stopwords = {
        "the", "and", "is", "in", "it", "of", "to", "for", "with", "on", "that", "this",
        "are", "was", "as", "at", "by", "an", "be", "from", "or", "which", "will", "has",
        "have", "had", "not", "but", "what", "all", "were", "when", "can", "said", "there",
        "they", "their", "one", "also", "about", "more", "out", "up", "into", "no", "if"
    }
    filtered_words = [w for w in words if w not in stopwords]
    if not filtered_words:
        return " ".join(sentences[:target_sentences])

    word_freq = Counter(filtered_words)
    max_freq = max(word_freq.values()) or 1
    scores = {}

    for i, sent in enumerate(sentences):
        sent_words = re.findall(r"\b[a-zA-Z]{3,}\b", sent.lower())
        score = sum(word_freq.get(w, 0) / max_freq for w in sent_words)
        # Position bias: introductory and concluding sentences carry higher weight
        if i == 0:
            score *= 1.3
        elif i < 3:
            score *= 1.15
        scores[i] = score / max(1, len(sent_words))

    top_indices = sorted(sorted(scores.keys(), key=lambda i: scores[i], reverse=True)[:target_sentences])
    return " ".join(sentences[i] for i in top_indices)


def _format_summary(summary_text: str, fmt: str = "paragraph") -> str:
    """Format summary as paragraph, bullet points, or TL;DR."""
    sentences = split_sentences(summary_text)
    if not sentences:
        return summary_text

    if fmt == "bullets":
        return "\n".join(f"• {s}" for s in sentences)
    elif fmt == "tldr":
        # Select the top 1 or 2 most descriptive sentences
        tldr_sents = sentences[:2]
        return "TL;DR: " + " ".join(tldr_sents)
    return summary_text


def _run_chunk(chunk: str, model_key: str, ratio: float) -> str:
    n = count_words(chunk)
    max_len = max(30, min(220, int(n * ratio * 1.4)))
    min_len = max(10, min(max_len - 5, int(max_len * 0.45)))
    out = _get_pipe(model_key)(
        chunk,
        max_length=max_len,
        min_length=min_len,
        do_sample=False,
        truncation=True,
    )
    return out[0]["summary_text"].strip()


def summarize(
    text: str,
    model: str = DEFAULT_MODEL,
    length: str = "medium",
    fmt: str = "paragraph",
    use_fallback: bool = True,
) -> dict:
    if model not in MODELS:
        raise ValueError(f"Unknown model '{model}'. Choose from: {', '.join(MODELS)}.")
    if length not in LENGTH_RATIOS:
        raise ValueError(f"Unknown length '{length}'. Choose from: {', '.join(LENGTH_RATIOS)}.")
    if fmt not in FORMATS:
        raise ValueError(f"Unknown format '{fmt}'. Choose from: {', '.join(FORMATS)}.")

    text = text.strip()
    n_words = count_words(text)
    if n_words < MIN_WORDS:
        raise ValueError(f"Add at least {MIN_WORDS} words to summarize (got {n_words}).")
    if n_words > MAX_WORDS:
        raise ValueError(f"Text is too long ({n_words} words). The limit is {MAX_WORDS}.")

    ratio = LENGTH_RATIOS[length]
    chunks = chunk_text(text)
    n_chunks = len(chunks)
    model_name = MODELS[model]
    used_fallback = False

    try:
        passes = 1
        summary = " ".join(_run_chunk(c, model, ratio) for c in chunks)

        # Multi-pass reduction for long articles
        while len(chunks) > 1 and count_words(summary) > CHUNK_WORDS and passes < 4:
            chunks = chunk_text(summary)
            summary = " ".join(_run_chunk(c, model, max(ratio, 0.5)) for c in chunks)
            passes += 1
    except Exception as e:
        if use_fallback:
            # Graceful fallback to extractive summarizer
            target_sentences = max(2, int(len(split_sentences(text)) * ratio))
            summary = _extractive_summarize(text, target_sentences=target_sentences)
            used_fallback = True
            model_name = f"{MODELS[model]} (Extractive fallback)"
        else:
            raise e

    formatted_summary = _format_summary(summary, fmt=fmt)

    return {
        "summary": formatted_summary,
        "model": model_name,
        "chunks": n_chunks,
        "format": fmt,
        "fallback": used_fallback,
    }
