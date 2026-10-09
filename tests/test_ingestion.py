import json

from ingestion.corpus.ingestion_manager import IngestionManager


def create_manifest(tmp_path):
    manifest_path = tmp_path / "manifest.json"

    manifest = {
        "islam.quran.arabic": {
            "corpus_id": "islam.quran.arabic",
            "title": "The Qur'an",
            "religion": "islam",
            "tradition": "islam",
            "source_type": "scripture",
            "original_language": "Arabic",
            "languages": ["Arabic"],
            "author": None,
            "translator": None,
            "publisher": None,
            "edition": None,
            "publication_year": None,
            "source_url": None,
            "license": None,
            "copyright_status": (
                "To be verified before redistribution"
            ),
            "local_path": str(tmp_path),
            "description": (
                "Structural test manifest."
            ),
            "tags": [
                "islam",
                "quran",
                "arabic",
                "scripture",
            ],
            "metadata": {},
        }
    }

    with manifest_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            manifest,
            file,
            indent=4,
        )

    return manifest_path


def create_valid_corpus(tmp_path):
    corpus_path = tmp_path / "quran.jsonl"

    records = [
        {
            "passage_id": "quran.1.1",
            "corpus_id": "islam.quran.arabic",
            "source_id": "islam.scripture.quran",
            "text": "STRUCTURAL TEST PASSAGE 1",
            "language": "Arabic",
            "reference": "Qur'an 1:1",
            "chapter": 1,
            "verse": 1,
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
        },
    ]

    with corpus_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for record in records:
            file.write(
                json.dumps(record)
                + "\n"
            )

    return corpus_path


def test_load_manifest(tmp_path):
    manager = IngestionManager()

    manifest_path = create_manifest(tmp_path)

    manifest = manager.load_manifest(
        manifest_path
    )

    assert manifest.corpus_id == (
        "islam.quran.arabic"
    )

    assert manifest.title == "The Qur'an"
    assert manifest.religion == "islam"
    assert manifest.languages == ["Arabic"]


def test_successful_ingestion(tmp_path):
    manager = IngestionManager()

    manifest_path = create_manifest(tmp_path)
    corpus_path = create_valid_corpus(tmp_path)

    passages, report, provenance = manager.ingest(
        manifest_path=manifest_path,
        corpus_path=corpus_path,
        source_id="islam.scripture.quran",
    )

    assert len(passages) == 2

    assert report.total_records == 2
    assert report.successful_records == 2
    assert report.failed_records == 0
    assert report.is_successful

    assert provenance is not None
    assert provenance.source_id == (
        "islam.scripture.quran"
    )

    assert provenance.file_sha256 is not None
    assert len(provenance.file_sha256) == 64

    assert provenance.local_file.endswith(
        "quran.jsonl"
    )


def test_ingestion_rejects_wrong_corpus_id(
    tmp_path,
):
    manager = IngestionManager()

    manifest_path = create_manifest(tmp_path)
    corpus_path = tmp_path / "wrong.jsonl"

    record = {
        "passage_id": "wrong.1",
        "corpus_id": "wrong.corpus",
        "source_id": "islam.scripture.quran",
        "text": "STRUCTURAL TEST PASSAGE",
        "language": "Arabic",
        "reference": "Wrong 1:1",
        "chapter": 1,
        "verse": 1,
    }

    with corpus_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(record)
            + "\n"
        )

    passages, report, provenance = manager.ingest(
        manifest_path=manifest_path,
        corpus_path=corpus_path,
        source_id="islam.scripture.quran",
    )

    assert passages == []
    assert report.successful_records == 0
    assert report.failed_records == 1
    assert len(report.errors) == 1

    assert provenance is not None


def test_ingestion_rejects_wrong_source_id(
    tmp_path,
):
    manager = IngestionManager()

    manifest_path = create_manifest(tmp_path)
    corpus_path = tmp_path / "wrong_source.jsonl"

    record = {
        "passage_id": "quran.1.1",
        "corpus_id": "islam.quran.arabic",
        "source_id": "wrong.source",
        "text": "STRUCTURAL TEST PASSAGE",
        "language": "Arabic",
        "reference": "Qur'an 1:1",
        "chapter": 1,
        "verse": 1,
    }

    with corpus_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(record)
            + "\n"
        )

    passages, report, provenance = manager.ingest(
        manifest_path=manifest_path,
        corpus_path=corpus_path,
        source_id="islam.scripture.quran",
    )

    assert passages == []
    assert report.successful_records == 0
    assert report.failed_records == 1
    assert len(report.errors) == 1

    assert provenance is not None


def test_ingestion_handles_invalid_json(
    tmp_path,
):
    manager = IngestionManager()

    manifest_path = create_manifest(tmp_path)
    corpus_path = tmp_path / "invalid.jsonl"

    with corpus_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write("{invalid json}\n")

    passages, report, provenance = manager.ingest(
        manifest_path=manifest_path,
        corpus_path=corpus_path,
        source_id="islam.scripture.quran",
    )

    assert passages == []
    assert report.successful_records == 0
    assert report.failed_records == 1
    assert len(report.errors) == 1

    assert provenance is not None


def test_ingestion_handles_missing_file(
    tmp_path,
):
    manager = IngestionManager()

    manifest_path = create_manifest(tmp_path)
    missing_corpus = (
        tmp_path / "does_not_exist.jsonl"
    )

    passages, report, provenance = manager.ingest(
        manifest_path=manifest_path,
        corpus_path=missing_corpus,
        source_id="islam.scripture.quran",
    )

    assert passages == []

    assert report.successful_records == 0
    assert report.failed_records == 1
    assert len(report.errors) == 1

    assert provenance is None


def test_ingestion_report_metadata(tmp_path):
    manager = IngestionManager()

    manifest_path = create_manifest(tmp_path)
    corpus_path = create_valid_corpus(tmp_path)

    _, report, provenance = manager.ingest(
        manifest_path=manifest_path,
        corpus_path=corpus_path,
        source_id="islam.scripture.quran",
    )

    assert provenance is not None

    assert report.metadata["title"] == (
        "The Qur'an"
    )

    assert report.metadata["religion"] == (
        "islam"
    )

    assert report.metadata["tradition"] == (
        "islam"
    )

    assert report.metadata["source_type"] == (
        "scripture"
    )

    assert report.metadata["languages"] == [
        "Arabic"
    ]

    assert report.metadata["source_id"] == (
        "islam.scripture.quran"
    )

    assert report.metadata["manifest_path"] == (
        str(manifest_path)
    )

    assert report.metadata["corpus_path"] == (
        str(corpus_path)
    )