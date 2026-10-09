from pathlib import Path

from ingestion.corpus.provenance_builder import ProvenanceBuilder


def test_provenance_builder_records_sha256(tmp_path: Path):
    corpus_file = tmp_path / "corpus.jsonl"

    corpus_file.write_text(
        '{"test": "FaithAI"}\n',
        encoding="utf-8",
    )

    provenance = ProvenanceBuilder.build(
        provenance_id="prov.test.001",
        source_id="test.source",
        title="Test Corpus",
        source_type="scripture",
        corpus_file=corpus_file,
    )

    assert provenance.provenance_id == "prov.test.001"
    assert provenance.source_id == "test.source"
    assert provenance.local_file == str(corpus_file)

    assert provenance.file_sha256 is not None
    assert len(provenance.file_sha256) == 64

    assert provenance.verification_status == "unverified"


def test_provenance_builder_creates_valid_record(tmp_path: Path):
    corpus_file = tmp_path / "corpus.jsonl"

    corpus_file.write_text(
        "FaithAI structural test",
        encoding="utf-8",
    )

    provenance = ProvenanceBuilder.build(
        provenance_id="prov.test.002",
        source_id="test.source",
        title="Test Corpus",
        source_type="scripture",
        corpus_file=corpus_file,
    )

    assert provenance.validate() == []