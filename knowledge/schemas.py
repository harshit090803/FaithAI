from typing import Optional
from pydantic import BaseModel, Field


class ReligiousPassage(BaseModel):
    source_id: str
    religion: str
    tradition: Optional[str] = None

    text_type: str
    title: str

    author: Optional[str] = None
    translator: Optional[str] = None

    language: Optional[str] = None
    original_language: Optional[str] = None

    original_text: Optional[str] = None
    translation: Optional[str] = None
    commentary: Optional[str] = None

    book: Optional[str] = None
    chapter: Optional[str] = None
    verse: Optional[str] = None
    page: Optional[str] = None

    edition: Optional[str] = None
    publication: Optional[str] = None

    source_url: Optional[str] = None
    copyright_status: Optional[str] = None

    provenance: Optional[str] = None

    metadata: dict = Field(default_factory=dict)