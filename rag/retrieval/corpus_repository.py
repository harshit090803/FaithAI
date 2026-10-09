import json
from pathlib import Path
from typing import Dict, List, Optional

from knowledge.sources.corpus_passage import CorpusPassage


class CorpusRepository:
    """
    Read-only repository for verified processed corpus passages.

    The repository does not modify the corpus. It only loads and
    retrieves already-validated passages.
    """

    def __init__(
        self,
        corpus_path: str | Path,
        expected_corpus_id: Optional[str] = None,
        expected_source_id: Optional[str] = None,
    ):
        self.corpus_path = Path(corpus_path)
        self.expected_corpus_id = expected_corpus_id
        self.expected_source_id = expected_source_id

        self._passages: Dict[str, CorpusPassage] = {}
        self._loaded = False

    def load(self) -> int:
        """Load the JSONL corpus into memory."""

        if not self.corpus_path.exists():
            raise FileNotFoundError(
                f"Corpus file not found: {self.corpus_path}"
            )

        if not self.corpus_path.is_file():
            raise ValueError(
                f"Corpus path is not a file: {self.corpus_path}"
            )

        passages: Dict[str, CorpusPassage] = {}

        with self.corpus_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()

                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON at line {line_number}: {exc}"
                    ) from exc

                passage = CorpusPassage(**record)

                errors = passage.validate()

                if errors:
                    raise ValueError(
                        f"Invalid passage at line {line_number}: "
                        f"{errors}"
                    )

                if (
                    self.expected_corpus_id is not None
                    and passage.corpus_id != self.expected_corpus_id
                ):
                    raise ValueError(
                        f"Unexpected corpus_id at line {line_number}: "
                        f"{passage.corpus_id}"
                    )

                if (
                    self.expected_source_id is not None
                    and passage.source_id != self.expected_source_id
                ):
                    raise ValueError(
                        f"Unexpected source_id at line {line_number}: "
                        f"{passage.source_id}"
                    )

                if passage.passage_id in passages:
                    raise ValueError(
                        f"Duplicate passage_id at line {line_number}: "
                        f"{passage.passage_id}"
                    )

                passages[passage.passage_id] = passage

        self._passages = passages
        self._loaded = True

        return len(self._passages)

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def get(self, passage_id: str) -> Optional[CorpusPassage]:
        """Retrieve a passage by its unique ID."""

        self._ensure_loaded()
        return self._passages.get(passage_id)

    def get_required(self, passage_id: str) -> CorpusPassage:
        """Retrieve a passage or raise KeyError."""

        passage = self.get(passage_id)

        if passage is None:
            raise KeyError(
                f"Passage not found: {passage_id}"
            )

        return passage

    def all(self) -> List[CorpusPassage]:
        """Return all loaded passages."""

        self._ensure_loaded()
        return list(self._passages.values())

    def count(self) -> int:
        """Return number of passages."""

        self._ensure_loaded()
        return len(self._passages)

    def clear(self) -> None:
        """Clear the in-memory repository."""

        self._passages.clear()
        self._loaded = False