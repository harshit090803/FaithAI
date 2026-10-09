from pathlib import Path
import json

import pytest

from knowledge.sources.corpus_manifest import (
    CorpusManifest,
    CorpusManifestRegistry,
)

from knowledge.sources.corpus_passage import (
    CorpusPassage,
)

from knowledge.sources.corpus_loader import (
    CorpusLoader,
)

from knowledge.sources.provenance import (
    SourceProvenance,
)

from knowledge.sources.provenance_registry import (
    ProvenanceRegistry,
)


# ============================================================
# Corpus Manifest Tests
# ============================================================


def create_valid_manifest():
    return CorpusManifest(
        corpus_id="islam.quran.arabic",
        title="The Qur'an",
        religion="islam",
        tradition="islam",
        source_type="scripture",
        original_language="Arabic",
        languages=["Arabic"],
        copyright_status="To be verified",
        description="Structural test corpus.",
        tags=[
            "islam",
            "quran",
            "arabic",
        ],
    )


def test_valid_corpus_manifest():
    registry = CorpusManifestRegistry()

    manifest = create_valid_manifest()

    errors = registry.validate(manifest)

    assert errors == []


def test_invalid_corpus_manifest():
    registry = CorpusManifestRegistry()

    manifest = CorpusManifest(
        corpus_id="",
        title="",
        religion="",
        tradition="islam",
        source_type="scripture",
        original_language="Arabic",
        languages=["Arabic"],
    )

    errors = registry.validate(manifest)

    assert len(errors) > 0


def test_manifest_requires_languages():
    registry = CorpusManifestRegistry()

    manifest = create_valid_manifest()

    manifest.languages = []

    errors = registry.validate(manifest)

    assert (
        "languages must contain at least one language"
        in errors
    )


def test_manifest_registry_add():
    registry = CorpusManifestRegistry()

    manifest = create_valid_manifest()

    assert registry.add_corpus(manifest) is True

    assert (
        registry.get_corpus(
            "islam.quran.arabic"
        )
        is not None
    )


def test_manifest_registry_duplicate():
    registry = CorpusManifestRegistry()

    manifest = create_valid_manifest()

    registry.add_corpus(manifest)

    with pytest.raises(ValueError):
        registry.add_corpus(manifest)


# ============================================================
# Corpus Passage Tests
# ============================================================


def create_valid_passage():
    return CorpusPassage(
        passage_id="quran.1.1",
        corpus_id="islam.quran.arabic",
        source_id="islam.scripture.quran",
        text="STRUCTURAL TEST PASSAGE",
        language="Arabic",
        reference="Qur'an 1:1",
        chapter=1,
        verse=1,
        original_text="STRUCTURAL TEST PASSAGE",
        original_language="Arabic",
    )


def test_valid_corpus_passage():
    passage = create_valid_passage()

    assert passage.is_valid()


def test_passage_requires_text():
    passage = create_valid_passage()

    passage.text = ""

    assert not passage.is_valid()


def test_passage_requires_valid_chapter():
    passage = create_valid_passage()

    passage.chapter = 0

    assert not passage.is_valid()


def test_passage_requires_valid_verse():
    passage = create_valid_passage()

    passage.verse = 0

    assert not passage.is_valid()


# ============================================================
# Corpus Loader Tests
# ============================================================


def test_valid_jsonl_loader(tmp_path):
    jsonl_file = tmp_path / "test.jsonl"

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

    with open(
        jsonl_file,
        "w",
        encoding="utf-8",
    ) as file:
        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

    loader = CorpusLoader(
        expected_corpus_id="islam.quran.arabic",
        expected_source_id="islam.scripture.quran",
    )

    passages, errors = loader.load_jsonl(
        jsonl_file
    )

    assert len(passages) == 2
    assert len(errors) == 0


def test_invalid_json(tmp_path):
    jsonl_file = tmp_path / "invalid.jsonl"

    with open(
        jsonl_file,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "{this is invalid json}\n"
        )

    loader = CorpusLoader()

    passages, errors = loader.load_jsonl(
        jsonl_file
    )

    assert len(passages) == 0
    assert len(errors) == 1


def test_loader_rejects_wrong_corpus_id():
    loader = CorpusLoader(
        expected_corpus_id="islam.quran.arabic"
    )

    record = {
        "passage_id": "test.001",
        "corpus_id": "wrong.corpus",
        "source_id": "islam.scripture.quran",
        "text": "STRUCTURAL TEST PASSAGE",
        "language": "Arabic",
    }

    with pytest.raises(ValueError):
        loader.load_record(record)


def test_loader_rejects_wrong_source_id():
    loader = CorpusLoader(
        expected_source_id="islam.scripture.quran"
    )

    record = {
        "passage_id": "test.001",
        "corpus_id": "islam.quran.arabic",
        "source_id": "wrong.source",
        "text": "STRUCTURAL TEST PASSAGE",
        "language": "Arabic",
    }

    with pytest.raises(ValueError):
        loader.load_record(record)


def test_loader_rejects_malformed_passage():
    loader = CorpusLoader()

    record = {
        "passage_id": "",
        "corpus_id": "islam.quran.arabic",
        "source_id": "islam.scripture.quran",
        "text": "",
        "language": "Arabic",
    }

    with pytest.raises(ValueError):
        loader.load_record(record)


def test_loader_single_valid_record():
    loader = CorpusLoader()

    record = {
        "passage_id": "quran.1.1",
        "corpus_id": "islam.quran.arabic",
        "source_id": "islam.scripture.quran",
        "text": "STRUCTURAL TEST PASSAGE",
        "language": "Arabic",
        "reference": "Qur'an 1:1",
        "chapter": 1,
        "verse": 1,
    }

    passage = loader.load_record(record)

    assert passage.passage_id == "quran.1.1"

    assert (
        passage.corpus_id
        == "islam.quran.arabic"
    )

    assert (
        passage.source_id
        == "islam.scripture.quran"
    )


def test_loader_single_invalid_record():
    loader = CorpusLoader()

    record = {
        "passage_id": "",
        "corpus_id": "islam.quran.arabic",
        "source_id": "islam.scripture.quran",
        "text": "STRUCTURAL TEST PASSAGE",
        "language": "Arabic",
    }

    with pytest.raises(ValueError):
        loader.load_record(record)


# ============================================================
# Provenance Tests
# ============================================================


def create_valid_provenance():
    return SourceProvenance(
        provenance_id="prov.islam.quran.arabic",
        source_id="islam.scripture.quran",
        title="The Qur'an",
        source_type="scripture",
        original_language="Arabic",
        publication_language="Arabic",
        copyright_status="To be verified",
        verification_status="pending",
        description="Structural provenance record.",
        tags=[
            "islam",
            "quran",
            "arabic",
        ],
    )


def test_valid_provenance():
    provenance = create_valid_provenance()

    assert provenance.is_valid()


def test_provenance_requires_identity():
    provenance = create_valid_provenance()

    provenance.provenance_id = ""

    assert not provenance.is_valid()


def test_provenance_requires_valid_status():
    provenance = create_valid_provenance()

    provenance.verification_status = (
        "invalid_status"
    )

    assert not provenance.is_valid()


def test_verified_provenance_requires_verifier_and_date():
    provenance = create_valid_provenance()

    provenance.verification_status = "verified"

    assert not provenance.is_valid()


# ============================================================
# Provenance Registry Tests
# ============================================================


def test_provenance_registry_add():
    registry = ProvenanceRegistry()

    provenance = create_valid_provenance()

    registry.add_provenance(provenance)

    assert (
        registry.get_provenance(
            "prov.islam.quran.arabic"
        )
        is not None
    )


def test_provenance_registry_duplicate():
    registry = ProvenanceRegistry()

    provenance = create_valid_provenance()

    registry.add_provenance(provenance)

    with pytest.raises(ValueError):
        registry.add_provenance(provenance)


def test_provenance_registry_find_by_source():
    registry = ProvenanceRegistry()

    provenance = create_valid_provenance()

    registry.add_provenance(provenance)

    results = registry.list_by_source(
        "islam.scripture.quran"
    )

    assert len(results) == 1

    assert (
        results[0].provenance_id
        == "prov.islam.quran.arabic"
    )


def test_provenance_registry_find_by_status():
    registry = ProvenanceRegistry()

    provenance = create_valid_provenance()

    registry.add_provenance(provenance)

    results = registry.list_by_status(
        "pending"
    )

    assert len(results) == 1

    assert (
        results[0].verification_status
        == "pending"
    )


def test_provenance_registry_remove():
    registry = ProvenanceRegistry()

    provenance = create_valid_provenance()

    registry.add_provenance(provenance)

    removed = registry.remove_provenance(
        "prov.islam.quran.arabic"
    )

    assert removed is True

    assert (
        registry.get_provenance(
            "prov.islam.quran.arabic"
        )
        is None
    )