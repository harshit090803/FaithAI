import hashlib
import re
from dataclasses import dataclass, field
from typing import List

from knowledge.schemas import ReligiousPassage


@dataclass
class ReligiousChunk:
    """
    A searchable chunk derived from a ReligiousPassage.

    The original source reference is preserved so that
    RAG can later provide accurate citations.
    """

    chunk_id: str

    source_id: str
    religion: str
    tradition: str | None

    text_type: str
    title: str

    book: str | None
    chapter: str | None
    verse: str | None

    original_text: str | None
    normalized_text: str

    author: str | None = None
    translator: str | None = None

    language: str | None = None
    original_language: str | None = None

    chunk_index: int = 0
    total_chunks: int = 1

    metadata: dict = field(default_factory=dict)


class ReligiousChunker:
    """
    Structure-aware chunker for religious texts.

    Design principles:
    1. Preserve religious/source boundaries.
    2. Never modify the original text.
    3. Keep citation metadata attached to every chunk.
    4. Split only when a passage exceeds max_characters.
    """

    def __init__(self, max_characters: int = 1500):
        if max_characters <= 0:
            raise ValueError("max_characters must be greater than 0.")

        self.max_characters = max_characters

    @staticmethod
    def _generate_chunk_id(
        source_id: str,
        chunk_index: int,
        text: str,
    ) -> str:
        """
        Generate a deterministic chunk ID.
        """

        content = f"{source_id}:{chunk_index}:{text}"

        digest = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()[:16]

        return f"{source_id}_chunk_{digest}"

    def _split_text(self, text: str) -> List[str]:
        """
        Split an unusually long passage while trying to preserve
        natural paragraph and sentence boundaries.
        """

        if len(text) <= self.max_characters:
            return [text]

        # First try paragraph boundaries.
        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]

        chunks: List[str] = []
        current = ""

        for paragraph in paragraphs:

            # If a paragraph itself is too large, split it by sentences.
            if len(paragraph) > self.max_characters:

                sentences = re.split(
                    r"(?<=[.!?।؟])\s+",
                    paragraph
                )

                for sentence in sentences:
                    sentence = sentence.strip()

                    if not sentence:
                        continue

                    if (
                        current
                        and len(current) + 1 + len(sentence)
                        > self.max_characters
                    ):
                        chunks.append(current)
                        current = ""

                    if len(sentence) > self.max_characters:
                        # Last-resort word-based splitting.
                        words = sentence.split()

                        for word in words:
                            if (
                                current
                                and len(current) + 1 + len(word)
                                > self.max_characters
                            ):
                                chunks.append(current)
                                current = ""

                            current = (
                                f"{current} {word}".strip()
                            )

                    else:
                        current = (
                            f"{current} {sentence}".strip()
                        )

            else:
                if (
                    current
                    and len(current) + 2 + len(paragraph)
                    > self.max_characters
                ):
                    chunks.append(current)
                    current = ""

                current = (
                    f"{current}\n\n{paragraph}".strip()
                )

        if current:
            chunks.append(current)

        return chunks

    def chunk(
        self,
        passage: ReligiousPassage,
        normalized_text: str | None = None,
    ) -> List[ReligiousChunk]:
        """
        Convert one ReligiousPassage into one or more
        citation-preserving ReligiousChunk objects.
        """

        text = (
            normalized_text
            or passage.original_text
            or passage.translation
            or passage.commentary
        )

        if not text:
            raise ValueError(
                f"No usable text found for source: "
                f"{passage.source_id}"
            )

        # IMPORTANT:
        # We don't alter the original source text.
        normalized_text = text.strip()

        text_parts = self._split_text(normalized_text)

        total_chunks = len(text_parts)

        chunks: List[ReligiousChunk] = []

        for index, chunk_text in enumerate(text_parts):

            chunk_id = self._generate_chunk_id(
                passage.source_id,
                index,
                chunk_text,
            )

            metadata = dict(passage.metadata)

            metadata.update(
                {
                    "source_id": passage.source_id,
                    "religion": passage.religion,
                    "tradition": passage.tradition,
                    "text_type": passage.text_type,
                    "title": passage.title,
                    "book": passage.book,
                    "chapter": passage.chapter,
                    "verse": passage.verse,
                    "chunk_index": index,
                    "total_chunks": total_chunks,
                }
            )

            chunk = ReligiousChunk(
                chunk_id=chunk_id,
                source_id=passage.source_id,
                religion=passage.religion,
                tradition=passage.tradition,
                text_type=passage.text_type,
                title=passage.title,
                book=passage.book,
                chapter=passage.chapter,
                verse=passage.verse,
                original_text=passage.original_text,
                normalized_text=chunk_text,
                author=passage.author,
                translator=passage.translator,
                language=passage.language,
                original_language=passage.original_language,
                chunk_index=index,
                total_chunks=total_chunks,
                metadata=metadata,
            )

            chunks.append(chunk)

        return chunks


if __name__ == "__main__":
    # Test passage
    test_passage = ReligiousPassage(
        source_id="quran_002_047",
        religion="islam",
        tradition="islam",
        text_type="primary_scripture",
        title="Quran",
        book="Quran",
        chapter="2",
        verse="47",
        language="Arabic",
        original_language="Arabic",
        original_text="TEST_RECORD",
        translation=None,
        translator=None,
        commentary=None,
        edition=None,
        publication=None,
        source_url=None,
        copyright_status="to_be_verified",
        provenance="TEST_RECORD",
        metadata={
            "test": True
        },
    )

    chunker = ReligiousChunker(
        max_characters=1500
    )

    chunks = chunker.chunk(test_passage)

    print(f"Generated chunks: {len(chunks)}")

    for chunk in chunks:
        print()
        print("Chunk ID:", chunk.chunk_id)
        print("Source ID:", chunk.source_id)
        print("Religion:", chunk.religion)
        print("Book:", chunk.book)
        print("Chapter:", chunk.chapter)
        print("Verse:", chunk.verse)
        print("Chunk:", chunk.chunk_index + 1, "/", chunk.total_chunks)
        print("Text:", chunk.normalized_text)