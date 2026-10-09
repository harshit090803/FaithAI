from rag.retrieval.quran_repository import QuranRepository
from rag.retrieval.citation import CitationBuilder


def test_citation_from_quran_passage():
    repository = QuranRepository()

    passage = repository.get_verse(1, 1)

    citation = CitationBuilder.from_passage(
        passage,
        source_title="Tanzil Quran Text — Uthmani",
        provenance_id="provenance.islam.quran.arabic",
    )

    assert citation.passage_id == "quran.1.1"
    assert citation.reference == "Qur'an 1:1"
    assert citation.corpus_id == "islam.quran.arabic"
    assert citation.source_id == "islam.scripture.quran"
    assert citation.language == "Arabic"
    assert citation.source_title == "Tanzil Quran Text — Uthmani"
    assert citation.provenance_id == (
        "provenance.islam.quran.arabic"
    )


def test_citation_short_reference():
    repository = QuranRepository()

    passage = repository.get_verse(2, 255)

    citation = CitationBuilder.from_passage(passage)

    assert citation.short() == "Qur'an 2:255"


def test_citation_to_dict():
    repository = QuranRepository()

    passage = repository.get_verse(1, 1)

    citation = CitationBuilder.from_passage(
        passage,
        source_title="Tanzil Quran Text — Uthmani",
    )

    data = citation.to_dict()

    assert data["passage_id"] == "quran.1.1"
    assert data["reference"] == "Qur'an 1:1"
    assert data["corpus_id"] == "islam.quran.arabic"
    assert data["source_id"] == "islam.scripture.quran"
    assert data["language"] == "Arabic"
