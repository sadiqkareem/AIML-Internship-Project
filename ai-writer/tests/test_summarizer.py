"""Unit tests for summarizer splitting, chunking, and formatting."""
import pytest
import summarizer


def test_split_sentences():
    text = "Hello world! This is a test. How are you doing today? Great to see you."
    sents = summarizer.split_sentences(text)
    assert len(sents) == 4
    assert sents[0] == "Hello world!"
    assert sents[1] == "This is a test."


def test_split_sentences_abbreviations():
    text = "Dr. Smith and Mr. Jones met in the U.S. to discuss AI algorithms at OpenAI Inc. It was productive."
    sents = summarizer.split_sentences(text)
    # Should not split on Dr., Mr., U.S., or Inc.
    assert len(sents) == 2
    assert "Dr. Smith" in sents[0]
    assert "U.S." in sents[0]
    assert sents[1] == "It was productive."


def test_chunk_text():
    # Construct 10 sentences with ~10 words each = ~100 words total
    sentences = [f"This is test sentence number {i} containing ten simple words here." for i in range(1, 11)]
    text = " ".join(sentences)
    chunks = summarizer.chunk_text(text, max_words=30)
    assert len(chunks) > 1
    for chunk in chunks:
        assert summarizer.count_words(chunk) <= 35


def test_extractive_fallback():
    article = (
        "Artificial intelligence is transforming industries worldwide with extraordinary breakthroughs. "
        "Autonomous vehicles and neural networks are improving everyday convenience. "
        "Natural language processing allows computers to understand and generate human text seamlessly. "
        "However, ethical considerations, security, and safety remain critical challenges for AI development. "
        "Researchers across academia and industry are collaborating to build responsible artificial intelligence systems."
    )
    summary = summarizer._extractive_summarize(article, target_sentences=2)
    assert len(summary) > 0
    sents = summarizer.split_sentences(summary)
    assert len(sents) == 2


def test_format_summary():
    raw = "First main finding here. Second key breakthrough reported. Third next step planned."
    # Paragraph
    p = summarizer._format_summary(raw, fmt="paragraph")
    assert p == raw

    # Bullets
    b = summarizer._format_summary(raw, fmt="bullets")
    assert "• First main finding here." in b
    assert "• Second key breakthrough reported." in b

    # TL;DR
    tldr = summarizer._format_summary(raw, fmt="tldr")
    assert tldr.startswith("TL;DR:")


def test_summarize_validation():
    # Too short
    with pytest.raises(ValueError, match="Add at least"):
        summarizer.summarize("Too short text.")

    # Invalid model
    with pytest.raises(ValueError, match="Unknown model"):
        summarizer.summarize("This text has enough words to bypass the minimum length test easily. " * 5, model="invalid-model")

    # Invalid length
    with pytest.raises(ValueError, match="Unknown length"):
        summarizer.summarize("This text has enough words to bypass the minimum length test easily. " * 5, length="ultra-huge")
