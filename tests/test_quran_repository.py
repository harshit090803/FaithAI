from rag.retrieval.quran_repository import QuranRepository


def test_quran_repository_loads_complete_corpus():
    repository = QuranRepository()

    assert repository.load() == 6236
    assert repository.count() == 6236


def test_get_first_verse():
    repository = QuranRepository()

    passage = repository.get_verse(1, 1)

    assert passage.passage_id == "quran.1.1"
    assert passage.reference == "Qur'an 1:1"
    assert passage.chapter == 1
    assert passage.verse == 1
    assert passage.language == "Arabic"
    assert passage.text == "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"


def test_get_specific_verse():
    repository = QuranRepository()

    passage = repository.get_verse(2, 255)

    assert passage.passage_id == "quran.2.255"
    assert passage.reference == "Qur'an 2:255"
    assert passage.chapter == 2
    assert passage.verse == 255
    assert passage.text


def test_get_surah():
    repository = QuranRepository()

    passages = repository.get_surah(1)

    assert len(passages) == 7

    for index, passage in enumerate(passages, 1):
        assert passage.chapter == 1
        assert passage.verse == index


def test_invalid_surah():
    repository = QuranRepository()

    try:
        repository.get_surah(115)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_missing_verse():
    repository = QuranRepository()

    try:
        repository.get_verse(1, 999)
        assert False, "Expected KeyError"
    except KeyError:
        pass
