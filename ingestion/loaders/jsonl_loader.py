import json
from pathlib import Path
from typing import Iterator

from knowledge.schemas import ReligiousPassage


class JSONLLoader:
    """
    Loads ReligiousPassage records from a JSONL file.
    Each line in the JSONL file represents one passage.
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> Iterator[ReligiousPassage]:
        """
        Read the JSONL file and yield validated ReligiousPassage objects.
        """

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"JSONL file not found: {self.file_path}"
            )

        with self.file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):

                line = line.strip()

                # Ignore empty lines
                if not line:
                    continue

                try:
                    data = json.loads(line)

                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"Invalid JSON at line {line_number}: {error}"
                    ) from error

                try:
                    passage = ReligiousPassage(**data)

                except Exception as error:
                    raise ValueError(
                        f"Invalid ReligiousPassage at "
                        f"line {line_number}: {error}"
                    ) from error

                yield passage


if __name__ == "__main__":
    file_path = (
        "data/islam/raw/quran/original/"
        "quran_arabic.jsonl"
    )

    loader = JSONLLoader(file_path)

    passages = list(loader.load())

    print(f"Loaded passages: {len(passages)}")

    for passage in passages:
        print()
        print("Source ID:", passage.source_id)
        print("Book:", passage.book)
        print("Chapter:", passage.chapter)
        print("Verse:", passage.verse)
        print("Text:", passage.original_text)