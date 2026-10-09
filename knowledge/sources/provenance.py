"""
FaithAI — Source Provenance

Defines provenance metadata for religious corpora, editions,
translations, commentaries, and other source material.

Provenance allows FaithAI to answer:

    Where did this information come from?
    Which edition was used?
    Who translated it?
    Who published it?
    What language was it originally in?
    What is its copyright/license status?
    Has the source been verified?

Important:
    Provenance describes a source. It does not determine
    whether a theological claim is true.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class SourceProvenance:
    """
    Describes the provenance of a source or corpus.

    The object is intentionally independent from the actual
    religious text so that provenance can be tracked even
    before a corpus is ingested.
    """

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    provenance_id: str
    source_id: str

    # ---------------------------------------------------------
    # Source identity
    # ---------------------------------------------------------

    title: str
    source_type: str

    # Examples:
    # scripture
    # translation
    # commentary
    # scholarly_work
    # historical_source
    # academic_paper

    # ---------------------------------------------------------
    # Origin
    # ---------------------------------------------------------

    author: Optional[str] = None
    translator: Optional[str] = None
    editor: Optional[str] = None

    original_language: Optional[str] = None
    publication_language: Optional[str] = None

    # ---------------------------------------------------------
    # Publication
    # ---------------------------------------------------------

    publisher: Optional[str] = None
    edition: Optional[str] = None
    publication_year: Optional[int] = None

    # ---------------------------------------------------------
    # Digital source
    # ---------------------------------------------------------

    source_url: Optional[str] = None
    access_date: Optional[str] = None

    acquisition_method: Optional[str] = None
    acquisition_date: Optional[str] = None
    local_file: Optional[str] = None
    file_sha256: Optional[str] = None

    # ---------------------------------------------------------
    # Rights / licensing
    # ---------------------------------------------------------

    license: Optional[str] = None
    copyright_status: Optional[str] = None

    # Examples:
    # public_domain
    # copyrighted
    # permission_required
    # license_verified
    # unknown

    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------

    verification_status: str = "unverified"

    # Examples:
    # unverified
    # pending
    # verified
    # rejected

    verified_by: Optional[str] = None
    verification_date: Optional[str] = None

    # ---------------------------------------------------------
    # Notes
    # ---------------------------------------------------------

    description: Optional[str] = None
    notes: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    tags: List[str] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate(self) -> List[str]:
        """
        Validate provenance metadata.

        Returns:
            A list of validation errors.
            Empty list means valid.
        """

        errors: List[str] = []

        # -----------------------------------------------------
        # Identity validation
        # -----------------------------------------------------

        if not self.provenance_id.strip():
            errors.append(
                "provenance_id cannot be empty."
            )

        if not self.source_id.strip():
            errors.append(
                "source_id cannot be empty."
            )

        if not self.title.strip():
            errors.append(
                "title cannot be empty."
            )

        if not self.source_type.strip():
            errors.append(
                "source_type cannot be empty."
            )

        # -----------------------------------------------------
        # Verification status
        # -----------------------------------------------------

        valid_statuses = {
            "unverified",
            "pending",
            "verified",
            "rejected",
        }

        if self.verification_status not in valid_statuses:
            errors.append(
                "verification_status must be one of: "
                + ", ".join(sorted(valid_statuses))
            )

        # -----------------------------------------------------
        # Publication year
        # -----------------------------------------------------

        if (
            self.publication_year is not None
            and (
                self.publication_year < 0
                or self.publication_year > 2100
            )
        ):
            errors.append(
                "publication_year must be between "
                "0 and 2100."
            )

        # -----------------------------------------------------
        # Verified provenance requirements
        # -----------------------------------------------------

        if self.verification_status == "verified":

            if not self.verified_by:
                errors.append(
                    "verified_by is required when "
                    "verification_status is 'verified'."
                )

            if not self.verification_date:
                errors.append(
                    "verification_date is required when "
                    "verification_status is 'verified'."
                )

        # -----------------------------------------------------
        # SHA-256 file integrity validation
        # -----------------------------------------------------

        if self.file_sha256 is not None:

            if len(self.file_sha256) != 64:
                errors.append(
                    "file_sha256 must contain exactly 64 "
                    "hexadecimal characters."
                )

            elif any(
                character not in "0123456789abcdefABCDEF"
                for character in self.file_sha256
            ):
                errors.append(
                    "file_sha256 must contain only "
                    "hexadecimal characters."
                )

        return errors

    # ---------------------------------------------------------
    # Validity
    # ---------------------------------------------------------

    def is_valid(self) -> bool:
        """
        Return True if provenance metadata is valid.
        """

        return len(self.validate()) == 0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert provenance metadata to a dictionary.
        """

        return asdict(self)

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    def summary(self) -> str:
        """
        Return a concise provenance summary.
        """

        author = self.author or "Unknown author"

        year = (
            str(self.publication_year)
            if self.publication_year is not None
            else "Unknown year"
        )

        return (
            f"{self.title} — "
            f"{author} — "
            f"{year}"
        )


# =============================================================
# Demonstration / Structural Test
# =============================================================

if __name__ == "__main__":

    print("FaithAI Source Provenance")
    print("=" * 60)

    provenance = SourceProvenance(
        provenance_id="prov.islam.quran.arabic",
        source_id="islam.scripture.quran",
        title="The Qur'an",
        source_type="scripture",
        original_language="Arabic",
        publication_language="Arabic",
        copyright_status="To be verified",
        verification_status="pending",
        description=(
            "Structural provenance record for the "
            "Arabic Qur'an corpus."
        ),
        tags=[
            "islam",
            "quran",
            "arabic",
            "scripture",
        ],
    )

    errors = provenance.validate()

    if errors:
        print("✗ Provenance is invalid.")

        for error in errors:
            print(f"  - {error}")

    else:
        print("✓ Provenance is valid.")

    print()
    print("Provenance:")

    print(
        f"- ID: {provenance.provenance_id}"
    )

    print(
        f"- Source: {provenance.source_id}"
    )

    print(
        f"- Title: {provenance.title}"
    )

    print(
        f"- Type: {provenance.source_type}"
    )

    print(
        f"- Original language: "
        f"{provenance.original_language}"
    )

    print(
        f"- Copyright status: "
        f"{provenance.copyright_status}"
    )

    print(
        f"- Verification status: "
        f"{provenance.verification_status}"
    )

    print()
    print("Summary:")
    print(provenance.summary())

    print()
    print("Dictionary representation:")
    print(provenance.to_dict())

    print()
    print("Provenance test completed.")