from typing import List

from rag.embeddings.embedder import Embedder
from rag.embeddings.vector_store import InMemoryVectorStore
from rag.retrieval.evidence import EvidenceBuilder, EvidenceResult
from rag.retrieval.quran_repository import QuranRepository
from rag.retrieval.semantic_retriever import SemanticRetriever


class QuranSemanticRetriever(SemanticRetriever):
    """
    Semantic retriever for the processed Qur'an corpus.

    The retriever is intentionally dependent on interfaces/components
    rather than a specific embedding model or vector database.
    """

    def __init__(
        self,
        embedder: Embedder,
        vector_store: InMemoryVectorStore,
        repository: QuranRepository | None = None,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.repository = repository or QuranRepository()

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> List[EvidenceResult]:

        if not query or not query.strip():
            return []

        if limit <= 0:
            return []

        query_vector = self.embedder.embed(query)

        matches = self.vector_store.search(
            query_vector,
            limit=limit,
        )

        results = []

        for match in matches:
            passage = self.repository.get(match.item_id)

            if passage is None:
                raise KeyError(
                    f"Vector store references unknown passage: "
                    f"{match.item_id}"
                )

            evidence = EvidenceBuilder.from_passage(
                passage=passage,
                source_title="Tanzil Quran Text — Uthmani",
                provenance_id="provenance.islam.quran.arabic",
                score=match.score,
            )

            results.append(evidence)

        return results
