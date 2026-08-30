import json
from pathlib import Path

from knowledge.schemas import ReligiousPassage


def validate_jsonl(file_path: str) -> tuple[int, int]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    valid = 0
    invalid = 0

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
                ReligiousPassage(**record)
                valid += 1

            except Exception as error:
                invalid += 1
                print(
                    f"Invalid record at line {line_number}: {error}"
                )

    return valid, invalid


if __name__ == "__main__":
    file_path = "data/islam/raw/quran/original/quran_arabic.jsonl"

    valid, invalid = validate_jsonl(file_path)

    print(f"Valid records: {valid}")
    print(f"Invalid records: {invalid}")