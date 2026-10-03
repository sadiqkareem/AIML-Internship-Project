"""Unit tests for readability metrics and word counting."""
from readability import count_words, readability


def test_count_words():
    assert count_words("Hello world") == 2
    assert count_words("Don't hesitate to contact us at 100% efficiency.") == 8
    assert count_words("") == 0
    assert count_words("   \n\t   ") == 0


def test_readability_empty():
    res = readability("")
    assert res["words"] == 0
    assert res["sentences"] == 0
    assert res["flesch_reading_ease"] == 0.0
    assert res["grade_level"] == 0.0
    assert res["label"] == "n/a"
    assert res["characters"] == 0


def test_readability_standard_text():
    sample = (
        "The quick brown fox jumps over the lazy dog. "
        "Artificial intelligence and machine learning are revolutionizing the modern world. "
        "Simple and clear communication enables better collaboration among cross-functional engineering teams."
    )
    res = readability(sample)
    assert res["words"] > 20
    assert res["sentences"] == 3
    assert 0.0 <= res["flesch_reading_ease"] <= 100.0
    assert res["grade_level"] >= 0.0
    assert res["characters"] == len(sample)
    assert "reading_time_sec" in res
    assert "grade_label" in res


def test_syllable_estimation():
    # Simple words
    res_easy = readability("The cat sat on the mat. Dogs run and play.")
    # Complex multisyllabic academic prose
    res_hard = readability(
        "Epistemological differentiation necessitates multidimensional transcendental hermeneutics "
        "characteristic of post-structuralist ontological conceptualization."
    )
    assert res_easy["flesch_reading_ease"] > res_hard["flesch_reading_ease"]
