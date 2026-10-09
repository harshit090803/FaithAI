from dataclasses import dataclass
from typing import Optional

from knowledge.sources.corpus_passage import CorpusPassage

from .citation import CitationBuilder, PassageCitation


@dataclass(frozen=True)
class EvidenceResult:
    """
    A retrieved passage together with its citation metadata.
    """

    passage: CorpusPassage
    citation: PassageCitation
    score: Optional[float] = None

    @property
    def text(self) -> str:
        return self.passage.text

    @property
    def reference(self) -> str:
        return self.passage.reference

    def to_dict(self) -> dict:
        return {
            "passage": self.passage.to_dict(),
            "citation": self.citation.to_dict(),
            "score": self.score,
        }


class EvidenceBuilder:
    """
    Builds evidence objects from verified corpus passages.
    """

    @staticmethod
    def from_passage(
        passage: CorpusPassage,
        source_title: Optional[str] = None,
        provenance_id: Optional[str] = None,
        score: Optional[float] = None,
    ) -> EvidenceResult:

        citation = CitationBuilder.from_passage(
            passage=passage,
            source_title=source_title,
            provenance_id=provenance_id,
        )

        return EvidenceResult(
            passage=passage,
            citation=citation,
            score=score,
        )