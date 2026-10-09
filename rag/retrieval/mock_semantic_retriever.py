from typing import Dict, List, Tuple

from .evidence import EvidenceBuilder, EvidenceResult
from .quran_repository import QuranRepository
from .semantic_retriever import SemanticRetriever


class MockSemanticRetriever(SemanticRetriever):
    """
    Deterministic semantic-retrieval stub.

    This class exists only to validate the retrieval architecture.
    It does NOT perform real semantic similarity.
    """

    CONCEPT_MAP: Dict[str, List[Tuple[int, int, float]]] = {
        "patience": [
            (2, 153, 0.95),
            (3, 200, 0.91),
        ],
        "hardship": [
            (94, 5, 0.94),
            (94, 6, 0.93),
        ],
    }

    def __init__(
        self,
        repository: QuranRepository | None = None,
    ):
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

        query_lower = query.lower()

        matches = []

        for concept, references in self.CONCEPT_MAP.items():
            if concept in query_lower:
                matches.extend(references)

        matches.sort(
            key=lambda item: item[2],
            reverse=True,
        )

        results = []

        for surah, ayah, score in matches[:limit]:
            passage = self.repository.get_verse(
                surah,
                ayah,
            )

            evidence = EvidenceBuilder.from_passage(
                passage=passage,
                source_title="Tanzil Quran Text — Uthmani",
                provenance_id="provenance.islam.quran.arabic",
                score=score,
            )

            results.append(evidence)

        return results
