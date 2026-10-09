from pathlib import Path
from typing import List

from knowledge.sources.corpus_passage import CorpusPassage

from .corpus_repository import CorpusRepository


class QuranRepository(CorpusRepository):
    """
    Read-only repository for the processed Qur'an corpus.
    """

    EXPECTED_CORPUS_ID = "islam.quran.arabic"
    EXPECTED_SOURCE_ID = "islam.scripture.quran"

    def __init__(
        self,
        corpus_path: str | Path = (
            "data/islam/processed/quran/passages.jsonl"
        ),
    ):
        super().__init__(
            corpus_path=corpus_path,
            expected_corpus_id=self.EXPECTED_CORPUS_ID,
            expected_source_id=self.EXPECTED_SOURCE_ID,
        )

    def get_verse(
        self,
        surah: int,
        ayah: int,
    ) -> CorpusPassage:
        """Retrieve a specific Qur'an verse."""

        passage_id = f"quran.{surah}.{ayah}"

        passage = self.get_required(passage_id)

        if passage.chapter != surah or passage.verse != ayah:
            raise ValueError(
                f"Corpus integrity error for {passage_id}"
            )

        return passage

    def get_surah(self, surah: int) -> List[CorpusPassage]:
        """Retrieve all verses belonging to a Surah."""

        if not 1 <= surah <= 114:
            raise ValueError(
                f"Surah must be between 1 and 114: {surah}"
            )

        passages = [
            passage
            for passage in self.all()
            if passage.chapter == surah
        ]

        return sorted(
            passages,
            key=lambda passage: passage.verse,
        )