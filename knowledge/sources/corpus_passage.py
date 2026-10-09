"""
FaithAI — Corpus Passage Model

Defines the structured representation of an individual passage
belonging to a registered religious corpus.

A CorpusPassage connects:
    Corpus Manifest
        ↓
    Individual Passage
        ↓
    Source / Citation / Retrieval

This model is intentionally source-aware and preserves original
text and provenance information.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class CorpusPassage:
    """
    Represents one passage from a religious corpus.

    Example:
        Qur'an 1:1
        Bhagavad Gita 2:47
        Gospel of Matthew 5:3
    """

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    passage_id: str
    corpus_id: str
    source_id: str

    # ---------------------------------------------------------
    # Text
    # ---------------------------------------------------------

    text: str
    language: str

    # ---------------------------------------------------------
    # Reference information
    # ---------------------------------------------------------

    reference: Optional[str] = None

    book: Optional[str] = None
    chapter: Optional[int] = None
    section: Optional[str] = None
    verse: Optional[int] = None

    # ---------------------------------------------------------
    # Original/source text
    # ---------------------------------------------------------

    original_text: Optional[str] = None
    original_language: Optional[str] = None

    # ---------------------------------------------------------
    # Translation information
    # ---------------------------------------------------------

    translator: Optional[str] = None
    translation_id: Optional[str] = None

    # ---------------------------------------------------------
    # Commentary
    # ---------------------------------------------------------

    commentary: Optional[str] = None

    # ---------------------------------------------------------
    # Additional metadata
    # ---------------------------------------------------------

    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate(self) -> List[str]:
        """
        Validate the passage.

        Returns:
            A list of validation errors.
            An empty list means the passage is valid.
        """

        errors: List[str] = []

        if not self.passage_id.strip():
            errors.append("passage_id cannot be empty.")

        if not self.corpus_id.strip():
            errors.append("corpus_id cannot be empty.")

        if not self.source_id.strip():
            errors.append("source_id cannot be empty.")

        if not self.text.strip():
            errors.append("text cannot be empty.")

        if not self.language.strip():
            errors.append("language cannot be empty.")

        if self.chapter is not None and self.chapter < 1:
            errors.append("chapter must be greater than 0.")

        if self.verse is not None and self.verse < 1:
            errors.append("verse must be greater than 0.")

        if self.original_language is not None:
            if not self.original_language.strip():
                errors.append(
                    "original_language cannot be an empty string."
                )

        if self.translation_id is not None:
            if not self.translator:
                errors.append(
                    "translator should be provided when "
                    "translation_id is specified."
                )

        return errors

    def is_valid(self) -> bool:
        """
        Return True if the passage passes validation.
        """

        return len(self.validate()) == 0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the passage into a dictionary.
        """

        return asdict(self)

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    def summary(self) -> str:
        """
        Return a concise human-readable summary.
        """

        reference = self.reference or "No reference"

        return (
            f"{reference} | "
            f"{self.language} | "
            f"{self.passage_id}"
        )


# =============================================================
# Demonstration / Structural Test
# =============================================================

if __name__ == "__main__":

    print("FaithAI Corpus Passage")
    print("=" * 60)

    passage = CorpusPassage(
        passage_id="quran.1.1",
        corpus_id="islam.quran.arabic",
        source_id="islam.scripture.quran",
        text="STRUCTURAL TEST PASSAGE",
        language="Arabic",
        reference="Qur'an 1:1",
        chapter=1,
        verse=1,
        original_text="STRUCTURAL TEST PASSAGE",
        original_language="Arabic",
        metadata={
            "test": True
        },
        tags=[
            "quran",
            "surah-al-fatiha",
            "structural-test"
        ],
    )

    errors = passage.validate()

    if errors:
        print("✗ Corpus passage is invalid.")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Corpus passage is valid.")

    print()
    print("Passage:")
    print(f"- ID: {passage.passage_id}")
    print(f"- Corpus: {passage.corpus_id}")
    print(f"- Source: {passage.source_id}")
    print(f"- Reference: {passage.reference}")
    print(f"- Language: {passage.language}")
    print(f"- Chapter: {passage.chapter}")
    print(f"- Verse: {passage.verse}")
    print(f"- Text: {passage.text}")

    print()
    print("Dictionary representation:")
    print(passage.to_dict())

    print()
    print("Summary:")
    print(passage.summary())

    print()
    print("Corpus passage test completed.")