from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReligiousSource:
    """
    Represents a source used by FaithAI.

    A source may be:
        - Scripture
        - Translation
        - Commentary
        - Hadith collection
        - Scholarly work
        - Historical document
        - Manuscript
        - Academic publication
        - Dataset

    The source record describes where information came from.
    It does not itself determine whether a religious claim is true.
    """

    source_id: str

    title: str
    source_type: str

    religion: Optional[str] = None
    tradition: Optional[str] = None

    author: Optional[str] = None
    translator: Optional[str] = None

    language: Optional[str] = None
    publication_year: Optional[int] = None

    publisher: Optional[str] = None
    edition: Optional[str] = None

    url: Optional[str] = None

    license: Optional[str] = None
    copyright_status: Optional[str] = None

    description: Optional[str] = None

    metadata: Dict[str, str] = field(
        default_factory=dict
    )

    tags: List[str] = field(
        default_factory=list
    )