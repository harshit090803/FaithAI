
from dataclasses import dataclass

import pytest

from rag.retrieval.quran_hybrid_retriever import QuranHybridRetriever


@dataclass
class FakePassage:
    passage_id: str
    text: str


@dataclass
class FakeEvidence:
    passage: FakePassage
    score: float
    source_title: str = "Test source"
    provenance_id: str = "test.provenance"


class FakeLexicalRetriever:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def retrieve(
        self,
        query,
        limit=5,
        include_expansions=True,
    ):
        self.calls.append(
            {
                "query": query,
                "limit": limit,
                "include_expansions": include_expansions,
            }
        )
        return self.responses.get(query, [])[:limit]


def test_hybrid_keeps_direct_and_concept_channels_separate():
    direct = FakeEvidence(
        FakePassage("quran.4.96", "Original verse text A"),
        10.0,
    )
    concept = FakeEvidence(
        FakePassage("quran.3.134", "Original verse text B"),
        5.0,
    )

    fake = FakeLexicalRetriever(
        {
            "المغفرة": [direct],
            "العفو": [concept],
            "الصفح": [concept],
        }
    )

    retriever = QuranHybridRetriever(
        lexical_retriever=fake,
        concept_expansions={
            "المغفرة": {
                "العفو": 1.0,
                "الصفح": 0.9,
            }
        },
    )

    results = retriever.retrieve("المغفرة", limit=5)

    assert {
        result.passage.passage_id
        for result in results
    } == {
        "quran.4.96",
        "quran.3.134",
    }

    # The original query must use both lexical channels.
    assert any(
        call["query"] == "المغفرة"
        and call["include_expansions"] is False
        for call in fake.calls
    )

    assert any(
        call["query"] == "المغفرة"
        and call["include_expansions"] is True
        for call in fake.calls
    )

    # Concept terms must be searched without lexical expansions.
    assert any(
        call["query"] == "العفو"
        and call["include_expansions"] is False
        for call in fake.calls
    )

    assert any(
        call["query"] == "الصفح"
        and call["include_expansions"] is False
        for call in fake.calls
    )


def test_original_evidence_and_source_text_are_preserved():
    original_text = "Exact original source text"

    evidence = FakeEvidence(
        FakePassage("quran.4.96", original_text),
        10.0,
        source_title="Tanzil Quran Text — Uthmani",
        provenance_id="provenance.islam.quran.arabic",
    )

    fake = FakeLexicalRetriever(
        {"المغفرة": [evidence]}
    )

    retriever = QuranHybridRetriever(
        lexical_retriever=fake,
        concept_expansions={},
    )

    results = retriever.retrieve("المغفرة")

    assert len(results) == 1
    assert results[0].evidence is evidence
    assert results[0].passage.text == original_text

    assert results[0].evidence.source_title == (
        "Tanzil Quran Text — Uthmani"
    )

    assert results[0].evidence.provenance_id == (
        "provenance.islam.quran.arabic"
    )


def test_verse_found_by_multiple_channels_is_not_duplicated():
    shared = FakeEvidence(
        FakePassage("quran.24.22", "Original verse text"),
        8.0,
    )

    fake = FakeLexicalRetriever(
        {
            "المغفرة": [shared],
            "العفو": [shared],
        }
    )

    retriever = QuranHybridRetriever(
        lexical_retriever=fake,
        concept_expansions={
            "المغفرة": {
                "العفو": 1.0,
            }
        },
    )

    results = retriever.retrieve("المغفرة", limit=10)

    matching = [
        result
        for result in results
        if result.passage.passage_id == "quran.24.22"
    ]

    assert len(matching) == 1
    assert matching[0].lexical_rank == 1
    assert matching[0].concept_rank == 1


def test_empty_query_returns_no_results():
    fake = FakeLexicalRetriever({})
    retriever = QuranHybridRetriever(
        lexical_retriever=fake
    )

    assert retriever.retrieve("") == []
    assert fake.calls == []


def test_invalid_rrf_parameter_is_rejected():
    with pytest.raises(ValueError):
        QuranHybridRetriever(rrf_k=0)
