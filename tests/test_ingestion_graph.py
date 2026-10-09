import json

from ingestion.corpus.ingestion_manager import IngestionManager
from knowledge.knowledge_graph import ReligiousKnowledgeGraph
from knowledge.sources.religious_source import ReligiousSource


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
            "copyright_status": (
                "To be verified before redistribution"
            ),
            "local_path": str(tmp_path),
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


def create_corpus(tmp_path):
    corpus_path = tmp_path / "quran.jsonl"

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

    with corpus_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(record)
            + "\n"
        )

    return corpus_path


def test_ingestion_registers_provenance_in_graph(
    tmp_path,
):
    manager = IngestionManager()
    graph = ReligiousKnowledgeGraph()

    source = ReligiousSource(
        source_id="islam.scripture.quran",
        title="The Qur'an",
        source_type="scripture",
        religion="islam",
    )

    graph.add_source(source)

    manifest_path = create_manifest(tmp_path)
    corpus_path = create_corpus(tmp_path)

    passages, report, provenance = (
        manager.ingest_into_graph(
            graph=graph,
            manifest_path=manifest_path,
            corpus_path=corpus_path,
            source_id="islam.scripture.quran",
        )
    )

    assert len(passages) == 1
    assert report.is_successful

    assert provenance is not None

    stored = graph.get_provenance(
        provenance.provenance_id
    )

    assert stored is not None
    assert stored.source_id == (
        "islam.scripture.quran"
    )

    assert stored.file_sha256 == (
        provenance.file_sha256
    )

    assert len(graph.provenance.provenance) == 1