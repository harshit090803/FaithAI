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

def test_prayer_spelling_variants_share_canonical_form():
    from rag.retrieval.quran_lexical_retriever import ArabicNormalizer

    assert ArabicNormalizer.tokenize("الصلاة") == ["الصلوة"]
    assert ArabicNormalizer.tokenize("الصلوة") == ["الصلوة"]


def test_prayer_query_retrieves_known_verse():
    from rag.retrieval.quran_lexical_retriever import QuranLexicalRetriever

    retriever = QuranLexicalRetriever()
    results = retriever.retrieve("الصلاة", limit=100)

    assert any(
        result.passage.passage_id == "quran.11.114"
        for result in results
    )


def test_original_source_text_remains_unchanged():
    from rag.retrieval.quran_lexical_retriever import QuranLexicalRetriever

    retriever = QuranLexicalRetriever()
    passage = retriever.repository.get_required("quran.11.114")

    assert "وَأَقِمِ ٱلصَّلَوٰةَ" in passage.text
def test_same_document_token_is_not_double_counted():
    retriever = QuranLexicalRetriever()

    # These two query terms can both match the same document token.
    passage_id = "quran.3.133"
    query_terms = [
        ("المغفرة", 1.0),
        ("مغفرة", 0.45),
    ]

    score = retriever._score_document(passage_id, query_terms)

    # The document contains one matching token: "مغفرة".
    # Its evidence should contribute only once, at the strongest weight.
    token_score = retriever._idf("مغفرة")

    assert score == token_score
def test_duplicate_query_variants_use_strongest_weight():
    retriever = QuranLexicalRetriever()
    passage_id = "quran.3.133"

    score = retriever._score_document(
        passage_id,
        [
            ("المغفرة", 1.0),
            ("مغفرة", 0.45),
        ],
    )

    expected = retriever._idf("مغفرة")

    assert abs(score - expected) < 1e-9


def test_distinct_document_tokens_can_both_contribute():
    retriever = QuranLexicalRetriever()
    passage_id = "quran.4.96"

    score = retriever._score_document(
        passage_id,
        [
            ("مغفرة", 1.0),
            ("غفورا", 0.4),
        ],
    )

    expected = (
        retriever._idf("ومغفرة")
        + 0.4 * retriever._idf("غفورا")
    )

    assert abs(score - expected) < 1e-9


def test_duplicate_evidence_does_not_increase_score():
    retriever = QuranLexicalRetriever()
    passage_id = "quran.3.133"

    single = retriever._score_document(
        passage_id,
        [("المغفرة", 1.0)],
    )

    duplicated = retriever._score_document(
        passage_id,
        [
            ("المغفرة", 1.0),
            ("مغفرة", 0.45),
            ("مغفرة", 0.30),
        ],
    )

    assert abs(single - duplicated) < 1e-9