import json
from pathlib import Path

p = Path("data/islam/processed/quran/passages.jsonl")
lines = p.read_text(encoding="utf-8").splitlines()

errors = []

for i, line in enumerate(lines, 1):
    record = json.loads(line)

    expected_id = f"quran.{record['chapter']}.{record['verse']}"
    expected_reference = f"Qur'an {record['chapter']}:{record['verse']}"

    if record["passage_id"] != expected_id:
        errors.append(
            f"Line {i}: ID mismatch: "
            f"{record['passage_id']} != {expected_id}"
        )

    if record["reference"] != expected_reference:
        errors.append(
            f"Line {i}: Reference mismatch: "
            f"{record['reference']} != {expected_reference}"
        )

print("Processed Quran JSONL validation")
print("--------------------------------")
print("Records:", len(lines))
print("Reference mismatches:", len(errors))

if errors:
    print("\nFirst errors:")
    for error in errors[:10]:
        print(error)
else:
    print("✓ All passage IDs and references are consistent")
