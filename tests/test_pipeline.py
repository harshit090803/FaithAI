import json

from ingestion.pipeline import IngestionPipeline
from ingestion.cleaners.text_cleaner import TextCleaner
from ingestion.chunkers.religious_chunker import ReligiousChunker
from knowledge.schemas import ReligiousPassage


def make_test_passage(**overrides):
    data = {
        "source_id": "test_001",
        "religion": "islam",
        "tradition": "islam",
        "text_type": "primary_scripture",
        "title": "Test Source",
        "book": "Test Book",
        "chapter": "1",
        "verse": "1",
        "language": "Arabic",
        "original_language": "Arabic",
        "original_text": "TEST_RECORD",
        "translation": None,
        "translator": None,
        "commentary": None,
        "edition": None,
        "publication": None,
        "source_url": None,
        "copyright_status": "test",
        "provenance": "test",
        "metadata": {},
    }

    data.update(overrides)

    return ReligiousPassage(**data)


def test_schema_accepts_valid_passage():
    passage = make_test_passage()

    assert passage.source_id == "test_001"
    assert passage.religion == "islam"
    assert passage.chapter == "1"
    assert passage.verse == "1"


def test_cleaner_preserves_original_text():
    text = "  TEST   TEXT  "

    result = TextCleaner.clean(text)

    assert result.original_text == text
    assert result.normalized_text == "TEST TEXT"


def test_chunker_creates_chunk():
    passage = make_test_passage()

    chunker = ReligiousChunker(
        max_characters=1500
    )

    chunks = chunker.chunk(passage)

    assert len(chunks) == 1
    assert chunks[0].source_id == "test_001"
    assert chunks[0].religion == "islam"
    assert chunks[0].chapter == "1"
    assert chunks[0].verse == "1"


def test_chunker_splits_long_text():
    long_text = "word " * 1000

    passage = make_test_passage(
        original_text=long_text
    )

    chunker = ReligiousChunker(
        max_characters=100
    )

    chunks = chunker.chunk(passage)

    assert len(chunks) > 1
    assert chunks[0].total_chunks == len(chunks)


def test_pipeline_creates_output(tmp_path):
    input_file = tmp_path / "input.jsonl"
    output_file = tmp_path / "output.jsonl"

    record = {
        "source_id": "test_001",
        "religion": "islam",
        "tradition": "islam",
        "text_type": "primary_scripture",
        "title": "Test Source",
        "book": "Test Book",
        "chapter": "1",
        "verse": "1",
        "language": "Arabic",
        "original_language": "Arabic",
        "original_text": "TEST_RECORD",
        "translation": None,
        "translator": None,
        "commentary": None,
        "edition": None,
        "publication": None,
        "source_url": None,
        "copyright_status": "test",
        "provenance": "test",
        "metadata": {},
    }

    input_file.write_text(
        json.dumps(
            record,
            ensure_ascii=False
        ) + "\n",
        encoding="utf-8"
    )

    pipeline = IngestionPipeline()

    result = pipeline.process_file(
        str(input_file),
        str(output_file)
    )

    assert result["passages_processed"] == 1
    assert result["chunks_generated"] == 1
    assert result["errors"] == 0

    assert output_file.exists()

    output_lines = (
        output_file
        .read_text(encoding="utf-8")
        .strip()
        .splitlines()
    )

    assert len(output_lines) == 1

    output_record = json.loads(
        output_lines[0]
    )

    assert output_record["source_id"] == "test_001"
    assert output_record["religion"] == "islam"
    assert output_record["chapter"] == "1"
    assert output_record["verse"] == "1"
    assert output_record["original_text"] == "TEST_RECORD"