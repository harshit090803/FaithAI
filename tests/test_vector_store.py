import pytest

from rag.embeddings.vector_store import InMemoryVectorStore


def test_vector_store_add_and_count():
    store = InMemoryVectorStore(dimension=3)

    store.add(
        "passage.1",
        [1.0, 0.0, 0.0],
    )

    assert store.count() == 1
    assert store.contains("passage.1")


def test_vector_store_search():
    store = InMemoryVectorStore(dimension=3)

    store.add(
        "x",
        [1.0, 0.0, 0.0],
    )

    store.add(
        "y",
        [0.0, 1.0, 0.0],
    )

    results = store.search(
        [1.0, 0.0, 0.0],
        limit=2,
    )

    assert len(results) == 2
    assert results[0].item_id == "x"
    assert results[0].score == pytest.approx(1.0)
    assert results[1].item_id == "y"
    assert results[1].score == pytest.approx(0.0)


def test_vector_store_orders_by_similarity():
    store = InMemoryVectorStore(dimension=2)

    store.add("low", [0.0, 1.0])
    store.add("high", [0.9, 0.1])

    results = store.search(
        [1.0, 0.0],
        limit=2,
    )

    assert results[0].item_id == "high"
    assert results[1].item_id == "low"
    assert results[0].score > results[1].score


def test_vector_store_limit():
    store = InMemoryVectorStore(dimension=2)

    store.add("a", [1.0, 0.0])
    store.add("b", [0.0, 1.0])
    store.add("c", [1.0, 1.0])

    results = store.search(
        [1.0, 0.0],
        limit=2,
    )

    assert len(results) == 2


def test_duplicate_item_rejected():
    store = InMemoryVectorStore(dimension=2)

    store.add("passage.1", [1.0, 0.0])

    with pytest.raises(ValueError):
        store.add("passage.1", [0.0, 1.0])


def test_wrong_dimension_rejected():
    store = InMemoryVectorStore(dimension=3)

    with pytest.raises(ValueError):
        store.add(
            "passage.1",
            [1.0, 0.0],
        )


def test_empty_search():
    store = InMemoryVectorStore(dimension=2)

    assert store.search(
        [1.0, 0.0]
    ) == []


def test_invalid_limit():
    store = InMemoryVectorStore(dimension=2)

    store.add("passage.1", [1.0, 0.0])

    assert store.search(
        [1.0, 0.0],
        limit=0,
    ) == []


def test_zero_vector_similarity():
    score = InMemoryVectorStore.cosine_similarity(
        [0.0, 0.0],
        [1.0, 0.0],
    )

    assert score == 0.0


def test_mismatched_vectors_rejected():
    with pytest.raises(ValueError):
        InMemoryVectorStore.cosine_similarity(
            [1.0, 0.0],
            [1.0],
        )
