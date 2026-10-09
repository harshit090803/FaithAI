from collections import Counter
from typing import Dict, List

from knowledge.sources.corpus_passage import CorpusPassage


class QuranReferenceValidator:
    """
    Validates the Surah/Ayah reference structure of the
    parsed Qur'an corpus.

    This validator checks whether the parsed passages match
    the expected number of verses in each of the 114 Surahs.

    It does not perform theological or interpretive validation.
    """

    EXPECTED_VERSE_COUNTS: Dict[int, int] = {
        1: 7,
        2: 286,
        3: 200,
        4: 176,
        5: 120,
        6: 165,
        7: 206,
        8: 75,
        9: 129,
        10: 109,
        11: 123,
        12: 111,
        13: 43,
        14: 52,
        15: 99,
        16: 128,
        17: 111,
        18: 110,
        19: 98,
        20: 135,
        21: 112,
        22: 78,
        23: 118,
        24: 64,
        25: 77,
        26: 227,
        27: 93,
        28: 88,
        29: 69,
        30: 60,
        31: 34,
        32: 30,
        33: 73,
        34: 54,
        35: 45,
        36: 83,
        37: 182,
        38: 88,
        39: 75,
        40: 85,
        41: 54,
        42: 53,
        43: 89,
        44: 59,
        45: 37,
        46: 35,
        47: 38,
        48: 29,
        49: 18,
        50: 45,
        51: 60,
        52: 49,
        53: 62,
        54: 55,
        55: 78,
        56: 96,
        57: 29,
        58: 22,
        59: 24,
        60: 13,
        61: 14,
        62: 11,
        63: 11,
        64: 18,
        65: 12,
        66: 12,
        67: 30,
        68: 52,
        69: 52,
        70: 44,
        71: 28,
        72: 28,
        73: 20,
        74: 56,
        75: 40,
        76: 31,
        77: 50,
        78: 40,
        79: 46,
        80: 42,
        81: 29,
        82: 19,
        83: 36,
        84: 25,
        85: 22,
        86: 17,
        87: 19,
        88: 26,
        89: 30,
        90: 20,
        91: 15,
        92: 21,
        93: 11,
        94: 8,
        95: 8,
        96: 19,
        97: 5,
        98: 8,
        99: 8,
        100: 11,
        101: 11,
        102: 8,
        103: 3,
        104: 9,
        105: 5,
        106: 4,
        107: 7,
        108: 3,
        109: 6,
        110: 3,
        111: 5,
        112: 4,
        113: 5,
        114: 6,
    }

    def validate(
        self,
        passages: List[CorpusPassage],
    ) -> List[str]:
        """
        Validate Surah/Ayah references.

        Returns:
            A list of validation errors.
            Empty list means all reference checks passed.
        """
        errors: List[str] = []

        if not passages:
            return ["No Quran passages were provided."]

        # ---------------------------------------------------------
        # 1. Count parsed passages by Surah
        # ---------------------------------------------------------

        actual_counts = Counter(
            passage.chapter
            for passage in passages
            if passage.chapter is not None
        )

        # ---------------------------------------------------------
        # 2. Check that all 114 Surahs exist
        # ---------------------------------------------------------

        for surah in range(1, 115):
            if surah not in actual_counts:
                errors.append(
                    f"Surah {surah}: no passages found."
                )

        # ---------------------------------------------------------
        # 3. Compare actual verse counts with expected counts
        # ---------------------------------------------------------

        for surah, expected_count in (
            self.EXPECTED_VERSE_COUNTS.items()
        ):
            actual_count = actual_counts.get(surah, 0)

            if actual_count != expected_count:
                errors.append(
                    f"Surah {surah}: expected "
                    f"{expected_count} verses, found "
                    f"{actual_count}."
                )

        # ---------------------------------------------------------
        # 4. Validate Ayah numbering within each Surah
        # ---------------------------------------------------------

        passages_by_surah: Dict[int, List[CorpusPassage]] = {}

        for passage in passages:
            if passage.chapter is None:
                continue

            passages_by_surah.setdefault(
                passage.chapter,
                [],
            ).append(passage)

        for surah in range(1, 115):
            expected_count = self.EXPECTED_VERSE_COUNTS[surah]

            surah_passages = passages_by_surah.get(
                surah,
                [],
            )

            actual_ayahs = sorted(
                passage.verse
                for passage in surah_passages
                if passage.verse is not None
            )

            expected_ayahs = list(
                range(
                    1,
                    expected_count + 1,
                )
            )

            if actual_ayahs != expected_ayahs:
                missing = sorted(
                    set(expected_ayahs)
                    - set(actual_ayahs)
                )

                unexpected = sorted(
                    set(actual_ayahs)
                    - set(expected_ayahs)
                )

                errors.append(
                    f"Surah {surah}: Ayah sequence mismatch. "
                    f"Missing={missing[:10]}, "
                    f"Unexpected={unexpected[:10]}."
                )

        # ---------------------------------------------------------
        # 5. Verify total passage count
        # ---------------------------------------------------------

        expected_total = sum(
            self.EXPECTED_VERSE_COUNTS.values()
        )

        actual_total = len(passages)

        if actual_total != expected_total:
            errors.append(
                f"Total verse count mismatch: expected "
                f"{expected_total}, found {actual_total}."
            )

        return errors

    def statistics(
        self,
        passages: List[CorpusPassage],
    ) -> Dict[str, object]:
        """
        Return reference-level statistics.
        """
        actual_counts = Counter(
            passage.chapter
            for passage in passages
            if passage.chapter is not None
        )

        expected_total = sum(
            self.EXPECTED_VERSE_COUNTS.values()
        )

        return {
            "expected_surahs": 114,
            "actual_surahs": len(actual_counts),
            "expected_total_verses": expected_total,
            "actual_total_verses": len(passages),
            "surah_counts_match": all(
                actual_counts.get(surah, 0)
                == expected_count
                for surah, expected_count
                in self.EXPECTED_VERSE_COUNTS.items()
            ),
        }


if __name__ == "__main__":
    from ingestion.corpus.tanzil_parser import TanzilParser

    print("Quran reference integrity validation")
    print("-------------------------------------")

    # ---------------------------------------------------------
    # Parse source corpus
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Validate references
    # ---------------------------------------------------------

    validator = QuranReferenceValidator()

    errors = validator.validate(passages)

    statistics = validator.statistics(passages)

    print(
        f"Expected total : "
        f"{statistics['expected_total_verses']}"
    )

    print(
        f"Actual total   : "
        f"{statistics['actual_total_verses']}"
    )

    print(
        f"Expected Surahs: "
        f"{statistics['expected_surahs']}"
    )

    print(
        f"Actual Surahs  : "
        f"{statistics['actual_surahs']}"
    )

    print(
        f"Counts match   : "
        f"{statistics['surah_counts_match']}"
    )

    print(
        f"Validation errors: {len(errors)}"
    )

    if errors:
        print()
        print("Reference validation errors")
        print("---------------------------")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print()
    print("✓ Quran reference integrity validation PASSED")