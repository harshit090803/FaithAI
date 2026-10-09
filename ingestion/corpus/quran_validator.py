from collections import Counter
from typing import Dict, List

from knowledge.sources.corpus_passage import CorpusPassage


class QuranStructuralValidator:
    """
    Validates the structural integrity of parsed Quran passages.

    This validator does NOT judge theology, interpretation, or
    textual authenticity. It only checks structural consistency
    of the ingested corpus.
    """

    EXPECTED_SURAH_COUNT = 114

    def validate(
        self,
        passages: List[CorpusPassage],
    ) -> List[str]:
        """
        Validate a collection of Quran passages.

        Returns:
            A list of validation errors.
            An empty list means the corpus passed all checks.
        """
        errors: List[str] = []

        if not passages:
            return ["No Quran passages were provided."]

        # ---------------------------------------------------------
        # 1. Basic passage validation
        # ---------------------------------------------------------

        for index, passage in enumerate(passages):
            passage_errors = passage.validate()

            for error in passage_errors:
                errors.append(
                    f"Passage {index + 1}: {error}"
                )

        # ---------------------------------------------------------
        # 2. Validate Surah numbers
        # ---------------------------------------------------------

        invalid_surahs = []

        for passage in passages:
            if passage.chapter is None:
                invalid_surahs.append(
                    passage.passage_id
                )
                continue

            if not 1 <= passage.chapter <= 114:
                invalid_surahs.append(
                    passage.passage_id
                )

        if invalid_surahs:
            errors.append(
                "Invalid Surah references found: "
                + ", ".join(invalid_surahs[:10])
            )

        # ---------------------------------------------------------
        # 3. Detect duplicate passage IDs
        # ---------------------------------------------------------

        passage_ids = [
            passage.passage_id
            for passage in passages
        ]

        duplicate_ids = [
            passage_id
            for passage_id, count in Counter(
                passage_ids
            ).items()
            if count > 1
        ]

        if duplicate_ids:
            errors.append(
                "Duplicate passage IDs found: "
                + ", ".join(duplicate_ids[:10])
            )

        # ---------------------------------------------------------
        # 4. Detect duplicate Surah/Ayah references
        # ---------------------------------------------------------

        references = [
            (
                passage.chapter,
                passage.verse,
            )
            for passage in passages
        ]

        duplicate_references = [
            reference
            for reference, count in Counter(
                references
            ).items()
            if count > 1
        ]

        if duplicate_references:
            formatted = [
                f"{surah}:{ayah}"
                for surah, ayah in duplicate_references
            ]

            errors.append(
                "Duplicate Surah/Ayah references found: "
                + ", ".join(formatted[:10])
            )

        # ---------------------------------------------------------
        # 5. Check that all 114 Surahs are represented
        # ---------------------------------------------------------

        surahs = {
            passage.chapter
            for passage in passages
            if passage.chapter is not None
        }

        missing_surahs = [
            surah
            for surah in range(
                1,
                self.EXPECTED_SURAH_COUNT + 1,
            )
            if surah not in surahs
        ]

        if missing_surahs:
            errors.append(
                "Missing Surahs: "
                + ", ".join(
                    str(surah)
                    for surah in missing_surahs
                )
            )

        # ---------------------------------------------------------
        # 6. Check for empty verse text
        # ---------------------------------------------------------

        empty_text = [
            passage.passage_id
            for passage in passages
            if not passage.text
        ]

        if empty_text:
            errors.append(
                "Passages with empty text: "
                + ", ".join(empty_text[:10])
            )

        # ---------------------------------------------------------
        # 7. Check source identity
        # ---------------------------------------------------------

        wrong_corpus = [
            passage.passage_id
            for passage in passages
            if passage.corpus_id
            != "islam.quran.arabic"
        ]

        if wrong_corpus:
            errors.append(
                "Passages with incorrect corpus_id: "
                + ", ".join(wrong_corpus[:10])
            )

        wrong_source = [
            passage.passage_id
            for passage in passages
            if passage.source_id
            != "islam.scripture.quran"
        ]

        if wrong_source:
            errors.append(
                "Passages with incorrect source_id: "
                + ", ".join(wrong_source[:10])
            )

        # ---------------------------------------------------------
        # 8. Check language
        # ---------------------------------------------------------

        wrong_language = [
            passage.passage_id
            for passage in passages
            if passage.language != "Arabic"
        ]

        if wrong_language:
            errors.append(
                "Passages with incorrect language: "
                + ", ".join(wrong_language[:10])
            )

        return errors

    def statistics(
        self,
        passages: List[CorpusPassage],
    ) -> Dict[str, object]:
        """
        Generate structural statistics for the corpus.
        """
        surah_counts = Counter(
            passage.chapter
            for passage in passages
            if passage.chapter is not None
        )

        return {
            "total_passages": len(passages),
            "surah_count": len(surah_counts),
            "first_passage": (
                passages[0].passage_id
                if passages
                else None
            ),
            "last_passage": (
                passages[-1].passage_id
                if passages
                else None
            ),
            "passages_per_surah": dict(
                sorted(surah_counts.items())
            ),
        }


if __name__ == "__main__":
    from ingestion.corpus.tanzil_parser import TanzilParser

    print("Quran structural validation")
    print("----------------------------")

    parser = TanzilParser()

    passages, parser_errors = parser.parse_file(
        "data/islam/raw/quran/quran-uthmani.txt"
    )

    if parser_errors:
        print(
            f"Parser errors: {len(parser_errors)}"
        )

        for error in parser_errors[:10]:
            print("-", error)

        raise SystemExit(1)

    print(
        f"Parsed passages: {len(passages)}"
    )

    validator = QuranStructuralValidator()

    errors = validator.validate(passages)

    statistics = validator.statistics(passages)

    print(
        f"Surahs found   : "
        f"{statistics['surah_count']}"
    )

    print(
        f"First passage  : "
        f"{statistics['first_passage']}"
    )

    print(
        f"Last passage   : "
        f"{statistics['last_passage']}"
    )

    print(
        f"Validation errors: {len(errors)}"
    )

    if errors:
        print()
        print("Validation errors")
        print("------------------")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print()
    print("✓ Quran structural validation PASSED")