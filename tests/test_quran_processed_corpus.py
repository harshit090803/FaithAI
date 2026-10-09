import json
from pathlib import Path


PROCESSED_QURAN = Path(
    "data/islam/processed/quran/passages.jsonl"
)


def test_processed_quran_jsonl_integrity():
    assert PROCESSED_QURAN.exists(), (
        f"Processed Quran corpus not found: {PROCESSED_QURAN}"
    )

    lines = PROCESSED_QURAN.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 6236

    for line_number, line in enumerate(lines, 1):
        record = json.loads(line)

        expected_id = (
            f"quran.{record['chapter']}.{record['verse']}"
        )

        expected_reference = (
            f"Qur'an {record['chapter']}:{record['verse']}"
        )

        assert record["passage_id"] == expected_id, (
            f"Line {line_number}: "
            f"invalid passage_id"
        )

        assert record["reference"] == expected_reference, (
            f"Line {line_number}: "
            f"invalid reference"
        )

        assert record["language"] == "Arabic"
        assert record["original_language"] == "Arabic"
        assert record["corpus_id"] == "islam.quran.arabic"
        assert record["source_id"] == "islam.scripture.quran"
        assert record["text"]