"""
FaithAI — Provenance Registry

Stores and manages SourceProvenance records.
"""

from typing import List, Optional

from .provenance import SourceProvenance


class ProvenanceRegistry:
    """
    Registry for source provenance records.
    """

    def __init__(self):
        self.provenance = {}

    # ---------------------------------------------------------
    # Add
    # ---------------------------------------------------------

    def add_provenance(
        self,
        record: SourceProvenance,
    ) -> bool:

        errors = record.validate()

        if errors:
            raise ValueError(
                "Invalid provenance record:\n"
                + "\n".join(errors)
            )

        if record.provenance_id in self.provenance:
            raise ValueError(
                f"Provenance already exists: "
                f"{record.provenance_id}"
            )

        self.provenance[
            record.provenance_id
        ] = record

        return True

    # ---------------------------------------------------------
    # Get
    # ---------------------------------------------------------

    def get_provenance(
        self,
        provenance_id: str,
    ) -> Optional[SourceProvenance]:

        return self.provenance.get(
            provenance_id
        )

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update_provenance(
        self,
        record: SourceProvenance,
    ) -> bool:

        if record.provenance_id not in self.provenance:
            raise KeyError(
                f"Provenance not found: "
                f"{record.provenance_id}"
            )

        errors = record.validate()

        if errors:
            raise ValueError(
                "Invalid provenance record:\n"
                + "\n".join(errors)
            )

        self.provenance[
            record.provenance_id
        ] = record

        return True

    # ---------------------------------------------------------
    # Remove
    # ---------------------------------------------------------

    def remove_provenance(
        self,
        provenance_id: str,
    ) -> bool:

        if provenance_id not in self.provenance:
            return False

        del self.provenance[
            provenance_id
        ]

        return True

    # ---------------------------------------------------------
    # List
    # ---------------------------------------------------------

    def list_all(self) -> List[SourceProvenance]:

        return list(
            self.provenance.values()
        )

    # ---------------------------------------------------------
    # Find by source
    # ---------------------------------------------------------

    def list_by_source(
        self,
        source_id: str,
    ) -> List[SourceProvenance]:

        return [
            record
            for record in self.provenance.values()
            if record.source_id == source_id
        ]

    # ---------------------------------------------------------
    # Find by verification status
    # ---------------------------------------------------------

    def list_by_status(
        self,
        status: str,
    ) -> List[SourceProvenance]:

        return [
            record
            for record in self.provenance.values()
            if record.verification_status == status
        ]

    # ---------------------------------------------------------
    # Verified records
    # ---------------------------------------------------------

    def verified_sources(
        self,
    ) -> List[SourceProvenance]:

        return self.list_by_status(
            "verified"
        )

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self) -> dict:

        records = self.list_all()

        statuses = {}

        for record in records:
            status = record.verification_status

            statuses[status] = (
                statuses.get(status, 0) + 1
            )

        return {
            "total": len(records),
            "verification_status": statuses,
        }


# =============================================================
# Demonstration / Structural Test
# =============================================================

if __name__ == "__main__":

    print("FaithAI Provenance Registry")
    print("=" * 60)

    registry = ProvenanceRegistry()

    quran_provenance = SourceProvenance(
        provenance_id="prov.islam.quran.arabic",
        source_id="islam.scripture.quran",
        title="The Qur'an",
        source_type="scripture",
        original_language="Arabic",
        publication_language="Arabic",
        copyright_status="To be verified",
        verification_status="pending",
        description=(
            "Structural provenance record for "
            "the Arabic Qur'an corpus."
        ),
        tags=[
            "islam",
            "quran",
            "arabic",
            "scripture",
        ],
    )

    registry.add_provenance(
        quran_provenance
    )

    print(
        f"Total provenance records: "
        f"{len(registry.list_all())}"
    )

    print()
    print("All provenance records:")

    for record in registry.list_all():
        print(
            f"- {record.title} "
            f"[{record.verification_status}] "
            f"({record.provenance_id})"
        )

    print()
    print("Islamic Qur'an provenance:")

    for record in registry.list_by_source(
        "islam.scripture.quran"
    ):
        print(
            f"- {record.title}"
        )

    print()
    print("Pending verification:")

    for record in registry.list_by_status(
        "pending"
    ):
        print(
            f"- {record.title}"
        )

    print()
    print("Statistics:")

    print(
        registry.statistics()
    )

    print()
    print("Provenance registry test completed.")