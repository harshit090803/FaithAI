from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SourcePassage:
    """
    A precise textual unit belonging to a ReligiousSource.

    Examples:

        Qur'an      -> Surah 112 -> Verse 1
        Bible       -> John      -> Chapter 3 -> Verse 16
        Bhagavad Gita -> Chapter 2 -> Verse 47
        Guru Granth Sahib -> Ang 1 -> Passage

    The model is deliberately generic so different traditions
    can use their own textual organization.
    """

    passage_id: str

    source_id: str

    text: str

    language: str

    # Human-readable reference
    reference: Optional[str] = None

    # Hierarchical textual location
    book: Optional[str] = None
    chapter: Optional[str] = None
    section: Optional[str] = None
    verse: Optional[str] = None

    # Original-language information
    original_text: Optional[str] = None
    original_language: Optional[str] = None

    # Translation information
    translator: Optional[str] = None
    translation_id: Optional[str] = None

    # Optional commentary / notes
    commentary: Optional[str] = None

    metadata: Dict[str, str] = field(
        default_factory=dict
    )

    tags: List[str] = field(
        default_factory=list
    )