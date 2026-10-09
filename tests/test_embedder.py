import pytest

from rag.embeddings.mock_embedder import MockEmbedder


def test_embedder_dimension():
    embedder = MockEmbedder()

    vector = embedder.embed("hello")

    assert len(vector) == embedder.dimension
    assert embedder.dimension == 16


def test_embedder_is_deterministic():
    embedder = MockEmbedder()

    first = embedder.embed("Quran")
    second = embedder.embed("Quran")

    assert first == second


def test_different_text_produces_different_vector():
    embedder = MockEmbedder()

    first = embedder.embed("patience")
    second = embedder.embed("hardship")

    assert first != second


def test_embedding_is_normalized():
    embedder = MockEmbedder()

    vector = embedder.embed("FaithAI")

    magnitude = sum(
        value * value
        for value in vector
    ) ** 0.5

    assert magnitude == pytest.approx(1.0)


def test_batch_embedding():
    embedder = MockEmbedder()

    texts = [
        "Quran",
        "patience",
        "hardship",
    ]

    vectors = embedder.embed_batch(texts)

    assert len(vectors) == 3

    for vector in vectors:
        assert len(vector) == embedder.dimension


def test_empty_text_rejected():
    embedder = MockEmbedder()

    with pytest.raises(ValueError):
        embedder.embed("")


def test_non_string_rejected():
    embedder = MockEmbedder()

    with pytest.raises(TypeError):
        embedder.embed(123)
