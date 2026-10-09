from rag.retrieval.quran_repository import QuranRepository
from rag.retrieval.evidence import EvidenceBuilder


def test_evidence_from_passage():
    repository = QuranRepository()

    passage = repository.get_verse(1, 1)

    evidence = EvidenceBuilder.from_passage(
        passage=passage,
        source_title="Tanzil Quran Text — Uthmani",
        provenance_id="provenance.islam.quran.arabic",
    )

    assert evidence.passage.passage_id == "quran.1.1"
    assert evidence.text == passage.text
    assert evidence.reference == "Qur'an 1:1"

    assert evidence.citation.passage_id == "quran.1.1"
    assert evidence.citation.reference == "Qur'an 1:1"
    assert evidence.citation.corpus_id == "islam.quran.arabic"
    assert evidence.citation.source_id == "islam.scripture.quran"

    assert (
        evidence.citation.provenance_id
        == "provenance.islam.quran.arabic"
    )


def test_evidence_with_score():
    repository = QuranRepository()

    passage = repository.get_verse(2, 255)

    evidence = EvidenceBuilder.from_passage(
        passage=passage,
        score=0.91,
    )

    assert evidence.score == 0.91
    assert evidence.reference == "Qur'an 2:255"


def test_evidence_without_score():
    repository = QuranRepository()

    passage = repository.get_verse(1, 1)

    evidence = EvidenceBuilder.from_passage(
        passage=passage,
    )

    assert evidence.score is None


def test_evidence_to_dict():
    repository = QuranRepository()

    passage = repository.get_verse(1, 1)

    evidence = EvidenceBuilder.from_passage(
        passage=passage,
        source_title="Tanzil Quran Text — Uthmani",
    )

    data = evidence.to_dict()

    assert "passage" in data
    assert "citation" in data
    assert "score" in data

    assert data["passage"]["passage_id"] == "quran.1.1"
    assert data["citation"]["reference"] == "Qur'an 1:1"
    assert data["score"] is None
