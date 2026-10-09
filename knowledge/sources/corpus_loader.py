"""
FaithAI — Corpus Loader

Loads structured JSONL corpus records and converts them into
validated CorpusPassage objects.

Pipeline:

    JSONL
      ↓
    Parse JSON
      ↓
    CorpusPassage
      ↓
    Validation
      ↓
    Loaded passages / errors
"""

import json
from pathlib import Path
from typing import List, Optional, Tuple

from .corpus_passage import CorpusPassage


class CorpusLoader:
    """
    Loads CorpusPassage records from JSONL files.
    """

    def __init__(
        self,
        expected_corpus_id: Optional[str] = None,
        expected_source_id: Optional[str] = None,
    ):
        self.expected_corpus_id = expected_corpus_id
        self.expected_source_id = expected_source_id

    # ---------------------------------------------------------
    # Load JSONL
    # ---------------------------------------------------------

    def load_jsonl(
        self,
        file_path: str,
    ) -> Tuple[List[CorpusPassage], List[str]]:
        """
        Load passages from a JSONL file.

        Returns:
            (passages, errors)

        Every non-empty line must contain one JSON object.
        """

        passages: List[CorpusPassage] = []
        errors: List[str] = []

        path = Path(file_path)

        if not path.exists():
            errors.append(f"File does not exist: {file_path}")
            return passages, errors

        if not path.is_file():
            errors.append(f"Path is not a file: {file_path}")
            return passages, errors

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:

                for line_number, line in enumerate(file, start=1):

                    line = line.strip()

                    # Ignore blank lines.
                    if not line:
                        continue

                    # -------------------------------------------------
                    # Parse JSON
                    # -------------------------------------------------

                    try:
                        record = json.loads(line)

                    except json.JSONDecodeError as exc:
                        errors.append(
                            f"Line {line_number}: "
                            f"Invalid JSON: {exc}"
                        )
                        continue

                    # -------------------------------------------------
                    # Ensure JSON object
                    # -------------------------------------------------

                    if not isinstance(record, dict):
                        errors.append(
                            f"Line {line_number}: "
                            "JSON record must be an object."
                        )
                        continue

                    # -------------------------------------------------
                    # Create CorpusPassage
                    # -------------------------------------------------

                    try:
                        passage = CorpusPassage(**record)

                    except TypeError as exc:
                        errors.append(
                            f"Line {line_number}: "
                            f"Invalid passage fields: {exc}"
                        )
                        continue

                    # -------------------------------------------------
                    # Validate passage
                    # -------------------------------------------------

                    validation_errors = passage.validate()

                    if validation_errors:
                        for error in validation_errors:
                            errors.append(
                                f"Line {line_number}: {error}"
                            )

                        continue

                    # -------------------------------------------------
                    # Validate corpus identity
                    # -------------------------------------------------

                    if (
                        self.expected_corpus_id is not None
                        and passage.corpus_id
                        != self.expected_corpus_id
                    ):
                        errors.append(
                            f"Line {line_number}: "
                            f"Expected corpus_id "
                            f"'{self.expected_corpus_id}', "
                            f"got '{passage.corpus_id}'."
                        )
                        continue

                    # -------------------------------------------------
                    # Validate source identity
                    # -------------------------------------------------

                    if (
                        self.expected_source_id is not None
                        and passage.source_id
                        != self.expected_source_id
                    ):
                        errors.append(
                            f"Line {line_number}: "
                            f"Expected source_id "
                            f"'{self.expected_source_id}', "
                            f"got '{passage.source_id}'."
                        )
                        continue

                    passages.append(passage)

        except OSError as exc:
            errors.append(
                f"Could not read file '{file_path}': {exc}"
            )

        return passages, errors

    # ---------------------------------------------------------
    # Load single JSON record
    # ---------------------------------------------------------

    def load_record(
        self,
        record: dict,
    ) -> CorpusPassage:
        """
        Convert a single dictionary into a validated
        CorpusPassage.

        Raises:
            ValueError if the record is invalid.
        """

        if not isinstance(record, dict):
            raise ValueError(
                "Corpus record must be a dictionary."
            )

        try:
            passage = CorpusPassage(**record)

        except TypeError as exc:
            raise ValueError(
                f"Invalid corpus passage fields: {exc}"
            ) from exc

        errors = passage.validate()

        if errors:
            raise ValueError(
                "Invalid corpus passage:\n"
                + "\n".join(
                    f"- {error}" for error in errors
                )
            )

        if (
            self.expected_corpus_id is not None
            and passage.corpus_id
            != self.expected_corpus_id
        ):
            raise ValueError(
                f"Expected corpus_id "
                f"'{self.expected_corpus_id}', "
                f"got '{passage.corpus_id}'."
            )

        if (
            self.expected_source_id is not None
            and passage.source_id
            != self.expected_source_id
        ):
            raise ValueError(
                f"Expected source_id "
                f"'{self.expected_source_id}', "
                f"got '{passage.source_id}'."
            )

        return passage


# =============================================================
# Demonstration / Structural Test
# =============================================================

if __name__ == "__main__":

    print("FaithAI Corpus Loader")
    print("=" * 60)

    # ---------------------------------------------------------
    # Create temporary structural JSONL test file
    # ---------------------------------------------------------

    test_directory = Path(
        "data/islam/raw/quran"
    )

    test_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    test_file = test_directory / "structural_test.jsonl"

    test_records = [
        {
            "passage_id": "quran.1.1",
            "corpus_id": "islam.quran.arabic",
            "source_id": "islam.scripture.quran",
            "text": "STRUCTURAL TEST PASSAGE 1",
            "language": "Arabic",
            "reference": "Qur'an 1:1",
            "chapter": 1,
            "verse": 1,
            "original_text": "STRUCTURAL TEST PASSAGE 1",
            "original_language": "Arabic",
            "metadata": {
                "test": True
            },
            "tags": [
                "structural-test"
            ],
        },
        {
            "passage_id": "quran.1.2",
            "corpus_id": "islam.quran.arabic",
            "source_id": "islam.scripture.quran",
            "text": "STRUCTURAL TEST PASSAGE 2",
            "language": "Arabic",
            "reference": "Qur'an 1:2",
            "chapter": 1,
            "verse": 2,
            "original_text": "STRUCTURAL TEST PASSAGE 2",
            "original_language": "Arabic",
            "metadata": {
                "test": True
            },
            "tags": [
                "structural-test"
            ],
        },
    ]

    with test_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        for record in test_records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(f"✓ Test JSONL created:")
    print(f"  {test_file}")

    # ---------------------------------------------------------
    # Load corpus
    # ---------------------------------------------------------

    loader = CorpusLoader(
        expected_corpus_id="islam.quran.arabic",
        expected_source_id="islam.scripture.quran",
    )

    passages, errors = loader.load_jsonl(
        str(test_file)
    )

    print()
    print("Loader results:")
    print(f"  Passages loaded : {len(passages)}")
    print(f"  Errors          : {len(errors)}")

    # ---------------------------------------------------------
    # Display passages
    # ---------------------------------------------------------

    print()

    for passage in passages:
        print(
            f"- {passage.passage_id} | "
            f"{passage.reference}"
        )

    # ---------------------------------------------------------
    # Display errors
    # ---------------------------------------------------------

    if errors:
        print()
        print("Errors:")

        for error in errors:
            print(f"- {error}")

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    print()

    if not errors:
        print(
            "✓ All structural corpus records "
            "loaded successfully."
        )
    else:
        print(
            "⚠ Corpus loaded with validation errors."
        )

    print()
    print("Corpus loader test completed.")