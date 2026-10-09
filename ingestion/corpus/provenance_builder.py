from datetime import date
from pathlib import Path

from knowledge.sources.provenance import SourceProvenance

from .file_hasher import FileHasher


class ProvenanceBuilder:
    """
    Builds SourceProvenance records for ingested corpus files.
    """

    @staticmethod
    def build(
        *,
        provenance_id: str,
        source_id: str,
        title: str,
        source_type: str,
        corpus_file: str | Path,
        acquisition_method: str = "local_file",
        license: str | None = None,
        copyright_status: str | None = None,
        original_language: str | None = None,
        publication_language: str | None = None,
        author: str | None = None,
        translator: str | None = None,
        publisher: str | None = None,
        edition: str | None = None,
        publication_year: int | None = None,
        source_url: str | None = None,
    ) -> SourceProvenance:
        """
        Create a provenance record and calculate the file SHA-256.
        """

        path = Path(corpus_file)

        file_sha256 = FileHasher.sha256(path)

        return SourceProvenance(
            provenance_id=provenance_id,
            source_id=source_id,
            title=title,
            source_type=source_type,
            author=author,
            translator=translator,
            original_language=original_language,
            publication_language=publication_language,
            publisher=publisher,
            edition=edition,
            publication_year=publication_year,
            source_url=source_url,
            access_date=date.today().isoformat(),
            acquisition_method=acquisition_method,
            acquisition_date=date.today().isoformat(),
            local_file=str(path),
            file_sha256=file_sha256,
            license=license,
            copyright_status=copyright_status,
            verification_status="unverified",
        )