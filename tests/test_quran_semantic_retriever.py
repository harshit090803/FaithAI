from rag.embeddings.mock_embedder import MockEmbedder
from rag.embeddings.vector_store import InMemoryVectorStore
from rag.retrieval.quran_repository import QuranRepository
from rag.retrieval.quran_semantic_retriever import (
    QuranSemanticRetriever,
)


def build_test_retriever():
    embedder = MockEmbedder()
    repository = QuranRepository()

    store = InMemoryVectorStore(
        dimension=embedder.dimension
    )

    for passage_id in [
        "quran.1.1",
        "quran.1.2",
        "quran.2.255",
    ]:
        passage = repository.get_required(passage_id)

        vector = embedder.embed(passage.text)

        store.add(
            passage_id,
            vector,
        )

    return QuranSemanticRetriever(
        embedder=embedder,
        vector_store=store,
        repository=repository,
    )


def test_quran_semantic_retriever_returns_evidence():
    retriever = build_test_retriever()

    results = retriever.retrieve(
        "بِسْمِ ٱللَّهِ",
        limit=2,
    )

    assert len(results) == 2

    for result in results:
        assert result.passage is not None
        assert result.citation is not None
        assert result.text
        assert result.reference.startswith("Qur'an")
        assert result.score is not None


def test_quran_semantic_retriever_ranks_matching_text_first():
    retriever = build_test_retriever()

    results = retriever.retrieve(
        "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
        limit=3,
    )

    assert len(results) == 3
    assert results[0].reference == "Qur'an 1:1"
    assert results[0].score >= results[1].score
    assert results[1].score >= results[2].score


def test_quran_semantic_retriever_respects_limit():
    retriever = build_test_retriever()

    results = retriever.retrieve(
        "Quran",
        limit=1,
    )

    assert len(results) == 1


def test_quran_semantic_retriever_empty_query():
    retriever = build_test_retriever()

    assert retriever.retrieve("") == []


def test_quran_semantic_retriever_invalid_limit():
    retriever = build_test_retriever()

    assert retriever.retrieve(
        "Quran",
        limit=0,
    ) == []


def test_quran_semantic_retriever_preserves_provenance():
    retriever = build_test_retriever()

    results = retriever.retrieve(
        "بِسْمِ ٱللَّهِ",
        limit=1,
    )

    evidence = results[0]

    assert (
        evidence.citation.corpus_id
        == "islam.quran.arabic"
    )

    assert (
        evidence.citation.source_id
        == "islam.scripture.quran"
    )

    assert (
        evidence.citation.provenance_id
        == "provenance.islam.quran.arabic"
    )


def test_unknown_vector_reference_is_rejected():
    embedder = MockEmbedder()
    store = InMemoryVectorStore(
        dimension=embedder.dimension
    )

    store.add(
        "quran.does.not.exist",
        embedder.embed("test"),
    )

    retriever = QuranSemanticRetriever(
        embedder=embedder,
        vector_store=store,
        repository=QuranRepository(),
    )

    try:
        retriever.retrieve("test")
        assert False, "Expected KeyError"
    except KeyError:
        pass
