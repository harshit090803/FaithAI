import json
import sys
from pathlib import Path

from ingestion.loaders.jsonl_loader import JSONLLoader
from ingestion.cleaners.text_cleaner import TextCleaner
from ingestion.chunkers.religious_chunker import ReligiousChunker


class IngestionPipeline:
    """
    End-to-end FaithAI ingestion pipeline.

    Flow:

        JSONL
          ↓
        Loader
          ↓
        ReligiousPassage
          ↓
        Cleaner
          ↓
        Normalized Text
          ↓
        Religious Chunker
          ↓
        Processed JSONL
    """

    def __init__(self, max_characters: int = 1500):
        self.cleaner = TextCleaner()

        self.chunker = ReligiousChunker(
            max_characters=max_characters
        )

    def process_file(
        self,
        input_path: str,
        output_path: str,
    ) -> dict:

        input_file = Path(input_path)
        output_file = Path(output_path)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        loader = JSONLLoader(
            str(input_file)
        )

        passages_processed = 0
        chunks_generated = 0
        errors = 0

        with output_file.open(
            "w",
            encoding="utf-8"
        ) as output:

            for passage in loader.load():

                passages_processed += 1

                try:
                    # Determine which source field contains
                    # the actual text.
                    source_text = (
                        passage.original_text
                        or passage.translation
                        or passage.commentary
                    )

                    if not source_text:
                        raise ValueError(
                            f"No text found for "
                            f"{passage.source_id}"
                        )

                    # Clean without modifying the source.
                    cleaned = self.cleaner.clean(
                        source_text
                    )

                    # Generate citation-preserving chunks.
                    chunks = self.chunker.chunk(
                        passage,
                        normalized_text=cleaned.normalized_text
                    )

                    for chunk in chunks:

                        record = {
                            "chunk_id": chunk.chunk_id,
                            "source_id": chunk.source_id,
                            "religion": chunk.religion,
                            "tradition": chunk.tradition,
                            "text_type": chunk.text_type,
                            "title": chunk.title,

                            "book": chunk.book,
                            "chapter": chunk.chapter,
                            "verse": chunk.verse,

                            "original_text": (
                                chunk.original_text
                            ),

                            "normalized_text": (
                                chunk.normalized_text
                            ),

                            "author": chunk.author,
                            "translator": chunk.translator,

                            "language": chunk.language,
                            "original_language": (
                                chunk.original_language
                            ),

                            "chunk_index": (
                                chunk.chunk_index
                            ),

                            "total_chunks": (
                                chunk.total_chunks
                            ),

                            "metadata": chunk.metadata,
                        }

                        output.write(
                            json.dumps(
                                record,
                                ensure_ascii=False
                            )
                            + "\n"
                        )

                        chunks_generated += 1

                except Exception as error:

                    errors += 1

                    print(
                        f"ERROR: {passage.source_id}"
                    )

                    print(
                        f"       {error}"
                    )

        return {
            "input": str(input_file),
            "output": str(output_file),
            "passages_processed": passages_processed,
            "chunks_generated": chunks_generated,
            "errors": errors,
        }


def main():

    # Default test input.
    input_path = (
        "data/islam/raw/quran/original/"
        "quran_arabic.jsonl"
    )

    # Processed output.
    output_path = (
        "data/islam/processed/"
        "quran_chunks.jsonl"
    )

    # Allow custom paths from command line.
    if len(sys.argv) >= 2:
        input_path = sys.argv[1]

    if len(sys.argv) >= 3:
        output_path = sys.argv[2]

    pipeline = IngestionPipeline(
        max_characters=1500
    )

    print("=" * 60)
    print("FaithAI Ingestion Pipeline")
    print("=" * 60)

    print(f"Input : {input_path}")
    print(f"Output: {output_path}")
    print()

    result = pipeline.process_file(
        input_path=input_path,
        output_path=output_path,
    )

    print("=" * 60)
    print("Pipeline completed")
    print("=" * 60)

    print(
        f"Passages processed : "
        f"{result['passages_processed']}"
    )

    print(
        f"Chunks generated   : "
        f"{result['chunks_generated']}"
    )

    print(
        f"Errors              : "
        f"{result['errors']}"
    )


if __name__ == "__main__":
    main()