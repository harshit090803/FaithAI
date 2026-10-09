import re
from typing import List

from .evidence import EvidenceBuilder, EvidenceResult
from .quran_repository import QuranRepository
from .retriever import Retriever


class QuranReferenceRetriever(Retriever):
    """
    Retrieves Qur'an verses using explicit references.

    Supported examples:
        Qur'an 1:1
        Quran 2:255
        2:255
    """

    REFERENCE_PATTERN = re.compile(
        r"(?:qur['’]?an\s*)?(\d{1,3})\s*:\s*(\d{1,3})",
        re.IGNORECASE,
    )

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

        match = self.REFERENCE_PATTERN.search(query)

        if not match:
            return []

        surah = int(match.group(1))
        ayah = int(match.group(2))

        passage = self.repository.get_verse(
            surah,
            ayah,
        )

        evidence = EvidenceBuilder.from_passage(
            passage=passage,
            source_title="Tanzil Quran Text — Uthmani",
            provenance_id="provenance.islam.quran.arabic",
        )

        return [evidence]
