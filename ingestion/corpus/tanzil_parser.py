from pathlib import Path
from typing import List, Tuple

from knowledge.sources.corpus_passage import CorpusPassage


class TanzilParser:
    """
    Parser for Tanzil Quran text files.

    Expected verse format:

        surah|ayah|text

    The Quran text is preserved exactly as stored in
    the original Tanzil source file.
    """

    def __init__(
        self,
        corpus_id: str = "islam.quran.arabic",
        source_id: str = "islam.scripture.quran",
        language: str = "Arabic",
    ):
        self.corpus_id = corpus_id
        self.source_id = source_id
        self.language = language

    def parse_file(
        self,
        file_path: str | Path,
    ) -> Tuple[List[CorpusPassage], List[str]]:
        """
        Parse a Tanzil Quran text file.

        Returns:
            passages:
                Successfully parsed Quran passages.

            errors:
                Parsing and validation errors.
        """
        path = Path(file_path)

        if not path.exists():
            return [], [f"File does not exist: {path}"]

        if not path.is_file():
            return [], [f"Path is not a file: {path}"]

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            return [], [
                f"File is not valid UTF-8: {exc}"
            ]
        except OSError as exc:
            return [], [
                f"Unable to read file: {exc}"
            ]

        passages: List[CorpusPassage] = []
        errors: List[str] = []

        lines = text.splitlines()

        in_copyright_block = False

        for line_number, line in enumerate(
            lines,
            start=1,
        ):
            # Ignore blank lines.
            if not line.strip():
                continue

            # Tanzil copyright block.
            if line.startswith(
                "# PLEASE DO NOT REMOVE OR CHANGE THIS COPYRIGHT BLOCK"
            ):
                in_copyright_block = True
                continue

            # Ignore the remainder of the known Tanzil
            # copyright/license block.
            if in_copyright_block:
                if line.startswith("#"):
                    continue

                # Unexpected non-comment content ends
                # the copyright block.
                in_copyright_block = False

            parts = line.split("|", 2)

            if len(parts) != 3:
                errors.append(
                    f"Line {line_number}: expected "
                    f"3 fields separated by '|', "
                    f"found {len(parts)}."
                )
                continue

            surah_text, ayah_text, verse_text = parts

            surah_text = surah_text.strip()
            ayah_text = ayah_text.strip()

            # IMPORTANT:
            # Do not strip or modify verse_text.
            if not surah_text:
                errors.append(
                    f"Line {line_number}: surah is empty."
                )
                continue

            if not ayah_text:
                errors.append(
                    f"Line {line_number}: ayah is empty."
                )
                continue

            if not verse_text:
                errors.append(
                    f"Line {line_number}: verse text is empty."
                )
                continue

            try:
                surah = int(surah_text)
                ayah = int(ayah_text)
            except ValueError:
                errors.append(
                    f"Line {line_number}: surah and ayah "
                    f"must be integers."
                )
                continue

            if surah < 1 or surah > 114:
                errors.append(
                    f"Line {line_number}: invalid surah "
                    f"number {surah}."
                )
                continue

            if ayah < 1:
                errors.append(
                    f"Line {line_number}: invalid ayah "
                    f"number {ayah}."
                )
                continue

            passage_id = f"quran.{surah}.{ayah}"

            passage = CorpusPassage(
                passage_id=passage_id,
                corpus_id=self.corpus_id,
                source_id=self.source_id,
                text=verse_text,
                language=self.language,
                reference=f"Qur'an {surah}:{ayah}",
                chapter=surah,
                verse=ayah,
                original_text=verse_text,
                original_language="Arabic",
                metadata={
                    "source_format": "tanzil_txt",
                    "source_line": line_number,
                },
                tags=[
                    "islam",
                    "quran",
                    "arabic",
                    "tanzil",
                ],
            )

            validation_errors = passage.validate()

            if validation_errors:
                for error in validation_errors:
                    errors.append(
                        f"Line {line_number}: {error}"
                    )
                continue

            passages.append(passage)

        return passages, errors

    def parse_record(
        self,
        line: str,
        line_number: int = 1,
    ) -> CorpusPassage:
        """
        Parse one Tanzil verse record.
        """
        parts = line.split("|", 2)

        if len(parts) != 3:
            raise ValueError(
                f"Line {line_number}: expected "
                f"3 fields separated by '|'."
            )

        surah_text, ayah_text, verse_text = parts

        surah_text = surah_text.strip()
        ayah_text = ayah_text.strip()

        if not surah_text:
            raise ValueError(
                f"Line {line_number}: surah is empty."
            )

        if not ayah_text:
            raise ValueError(
                f"Line {line_number}: ayah is empty."
            )

        if not verse_text:
            raise ValueError(
                f"Line {line_number}: verse text is empty."
            )

        try:
            surah = int(surah_text)
            ayah = int(ayah_text)
        except ValueError as exc:
            raise ValueError(
                f"Line {line_number}: surah and ayah "
                f"must be integers."
            ) from exc

        if surah < 1 or surah > 114:
            raise ValueError(
                f"Line {line_number}: invalid surah "
                f"number {surah}."
            )

        if ayah < 1:
            raise ValueError(
                f"Line {line_number}: invalid ayah "
                f"number {ayah}."
            )

        passage = CorpusPassage(
            passage_id=f"quran.{surah}.{ayah}",
            corpus_id=self.corpus_id,
            source_id=self.source_id,
            text=verse_text,
            language=self.language,
            reference=f"Qur'an {surah}:{ayah}",
            chapter=surah,
            verse=ayah,
            original_text=verse_text,
            original_language="Arabic",
            metadata={
                "source_format": "tanzil_txt",
                "source_line": line_number,
            },
            tags=[
                "islam",
                "quran",
                "arabic",
                "tanzil",
            ],
        )

        errors = passage.validate()

        if errors:
            raise ValueError(
                f"Line {line_number}: "
                + "; ".join(errors)
            )

        return passage


if __name__ == "__main__":
    parser = TanzilParser()

    passages, errors = parser.parse_file(
        "data/islam/raw/quran/quran-uthmani.txt"
    )

    print("Tanzil parser test")
    print("------------------")
    print("Passages:", len(passages))
    print("Errors  :", len(errors))

    if passages:
        first = passages[0]

        print()
        print("First passage")
        print("-------------")
        print("ID       :", first.passage_id)
        print("Reference:", first.reference)
        print("Language :", first.language)
        print("Text     :", first.text)

    if errors:
        print()
        print("First errors")
        print("------------")

        for error in errors[:10]:
            print("-", error)