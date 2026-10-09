from rag.retrieval.quran_lexical_retriever import (
    ArabicNormalizer,
    QuranLexicalRetriever,
)


def test_arabic_normalizer_removes_diacritics():
    text = "ٱلصَّبْرِ"

    normalized = ArabicNormalizer.normalize(text)

    assert normalized == "الصبر"


def test_arabic_normalizer_handles_alif_variants():
    text = "أَإِآٱ"

    normalized = ArabicNormalizer.normalize(text)

    assert normalized == "اااا"


def test_quran_lexical_retriever_loads_full_corpus():
    retriever = QuranLexicalRetriever()

    assert retriever.document_count == 6236
    assert retriever.vocabulary_size > 0


def test_quran_lexical_retriever_finds_exact_word():
    retriever = QuranLexicalRetriever()

    results = retriever.retrieve(
        "الصبر",
        limit=10,
    )

    assert results

    references = [
        result.passage.reference
        for result in results
    ]

    assert any(
        "2:153" in reference
        for reference in references
    )


def test_empty_query_returns_empty():
    retriever = QuranLexicalRetriever()

    assert retriever.retrieve("") == []


def test_invalid_limit_returns_empty():
    retriever = QuranLexicalRetriever()

    assert retriever.retrieve("الصبر", limit=0) == []