from rag.retrieval.mock_semantic_retriever import (
    MockSemanticRetriever,
)


def test_semantic_retriever_patience():
    retriever = MockSemanticRetriever()

    results = retriever.retrieve(
        "What does the Quran say about patience?"
    )

    assert len(results) == 2

    assert results[0].reference == "Qur'an 2:153"
    assert results[1].reference == "Qur'an 3:200"

    assert results[0].score == 0.95
    assert results[1].score == 0.91


def test_semantic_retriever_hardship():
    retriever = MockSemanticRetriever()

    results = retriever.retrieve(
        "What does the Quran say about hardship?"
    )

    assert len(results) == 2

    assert results[0].reference == "Qur'an 94:5"
    assert results[1].reference == "Qur'an 94:6"


def test_semantic_retriever_limit():
    retriever = MockSemanticRetriever()

    results = retriever.retrieve(
        "patience",
        limit=1,
    )

    assert len(results) == 1
    assert results[0].reference == "Qur'an 2:153"


def test_semantic_retriever_empty_query():
    retriever = MockSemanticRetriever()

    assert retriever.retrieve("") == []


def test_semantic_retriever_unknown_query():
    retriever = MockSemanticRetriever()

    results = retriever.retrieve(
        "quantum computing"
    )

    assert results == []


def test_semantic_results_have_evidence():
    retriever = MockSemanticRetriever()

    results = retriever.retrieve("patience")

    assert results

    for result in results:
        assert result.passage is not None
        assert result.citation is not None
        assert result.text
        assert result.reference.startswith("Qur'an")
        assert result.score is not None
