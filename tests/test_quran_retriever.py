from rag.retrieval.quran_retriever import QuranReferenceRetriever


def test_retrieve_quran_reference():
    retriever = QuranReferenceRetriever()

    results = retriever.retrieve("Qur'an 1:1")

    assert len(results) == 1

    evidence = results[0]

    assert evidence.reference == "Qur'an 1:1"
    assert evidence.passage.passage_id == "quran.1.1"
    assert evidence.citation.source_id == "islam.scripture.quran"


def test_retrieve_without_quran_word():
    retriever = QuranReferenceRetriever()

    results = retriever.retrieve("2:255")

    assert len(results) == 1
    assert results[0].reference == "Qur'an 2:255"


def test_retrieve_case_insensitive():
    retriever = QuranReferenceRetriever()

    results = retriever.retrieve("QURAN 1:1")

    assert len(results) == 1
    assert results[0].reference == "Qur'an 1:1"


def test_retrieve_empty_query():
    retriever = QuranReferenceRetriever()

    assert retriever.retrieve("") == []


def test_retrieve_non_reference_query():
    retriever = QuranReferenceRetriever()

    results = retriever.retrieve(
        "What does the Quran say about patience?"
    )

    assert results == []


def test_retrieve_invalid_limit():
    retriever = QuranReferenceRetriever()

    assert retriever.retrieve("Qur'an 1:1", limit=0) == []


def test_retrieve_specific_verse():
    retriever = QuranReferenceRetriever()

    results = retriever.retrieve("Please show Qur'an 2:255")

    assert len(results) == 1

    evidence = results[0]

    assert evidence.passage.chapter == 2
    assert evidence.passage.verse == 255
    assert evidence.reference == "Qur'an 2:255"
