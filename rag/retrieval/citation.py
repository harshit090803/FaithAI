from dataclasses import dataclass
from typing import Optional

from knowledge.sources.corpus_passage import CorpusPassage


@dataclass(frozen=True)
class PassageCitation:
    """
    Citation metadata for a retrieved religious passage.
    """

    passage_id: str
    reference: str
    corpus_id: str
    source_id: str
    language: str
    source_title: Optional[str] = None
    provenance_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "passage_id": self.passage_id,
            "reference": self.reference,
            "corpus_id": self.corpus_id,
            "source_id": self.source_id,
            "language": self.language,
            "source_title": self.source_title,
            "provenance_id": self.provenance_id,
        }

    def short(self) -> str:
        return self.reference


class CitationBuilder:
    """
    Builds citations from verified CorpusPassage objects.
    """

    @staticmethod
    def from_passage(
        passage: CorpusPassage,
        source_title: Optional[str] = None,
        provenance_id: Optional[str] = None,
    ) -> PassageCitation:

        return PassageCitation(
            passage_id=passage.passage_id,
            reference=passage.reference,
            corpus_id=passage.corpus_id,
            source_id=passage.source_id,
            language=passage.language,
            source_title=source_title,
            provenance_id=provenance_id,
        )
