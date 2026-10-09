from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class IngestionReport:
    """
    Stores the result of a corpus ingestion operation.
    """

    corpus_id: str

    total_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    skipped_records: int = 0

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    metadata: Dict[str, object] = field(default_factory=dict)

    @property
    def is_successful(self) -> bool:
        """
        Returns True when the ingestion completed without errors.
        """
        return self.failed_records == 0 and len(self.errors) == 0

    @property
    def processed_records(self) -> int:
        """
        Number of records successfully processed.
        """
        return self.successful_records

    def add_success(self) -> None:
        """Record one successfully processed passage."""
        self.total_records += 1
        self.successful_records += 1

    def add_failure(self, error: str) -> None:
        """Record one failed passage."""
        self.total_records += 1
        self.failed_records += 1
        self.errors.append(str(error))

    def add_skipped(self, warning: str = "") -> None:
        """Record one skipped passage."""
        self.total_records += 1
        self.skipped_records += 1

        if warning:
            self.warnings.append(str(warning))

    def add_warning(self, warning: str) -> None:
        """Add a non-fatal ingestion warning."""
        self.warnings.append(str(warning))

    def to_dict(self) -> Dict[str, object]:
        """Convert the report to a JSON-compatible dictionary."""
        return {
            "corpus_id": self.corpus_id,
            "total_records": self.total_records,
            "successful_records": self.successful_records,
            "failed_records": self.failed_records,
            "skipped_records": self.skipped_records,
            "processed_records": self.processed_records,
            "is_successful": self.is_successful,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }

    def summary(self) -> str:
        """Return a human-readable ingestion summary."""
        return (
            f"Corpus: {self.corpus_id}\n"
            f"Total records   : {self.total_records}\n"
            f"Successful      : {self.successful_records}\n"
            f"Failed          : {self.failed_records}\n"
            f"Skipped         : {self.skipped_records}\n"
            f"Warnings        : {len(self.warnings)}\n"
            f"Errors          : {len(self.errors)}\n"
            f"Status          : "
            f"{'SUCCESS' if self.is_successful else 'FAILED'}"
        )