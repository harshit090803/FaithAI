from pathlib import Path
from typing import List, Optional, Tuple

from knowledge.sources import provenance
from knowledge.sources.corpus_passage import CorpusPassage
from knowledge.sources.corpus_manifest import CorpusManifest
from knowledge.sources.corpus_loader import CorpusLoader
from knowledge.sources.provenance import SourceProvenance

from .ingestion_report import IngestionReport
from .manifest_loader import ManifestLoader
from .provenance_builder import ProvenanceBuilder

from knowledge.knowledge_graph import ReligiousKnowledgeGraph

class IngestionManager:
    """
    Coordinates corpus manifest loading, corpus ingestion,
    reporting, and provenance generation.
    """
    def ingest_into_graph(self, graph : ReligiousKnowledgeGraph, manifest_path : str, corpus_path : str, source_id : str):
        passages, report, provenance = self.ingest(
        manifest_path=manifest_path,
        corpus_path=corpus_path,
        source_id=source_id,
    )
        if provenance is not None:
            graph.add_provenance(provenance)
        return passages, report, provenance
    def __init__(self):
        self.manifest_loader = ManifestLoader()

    def load_manifest(self, manifest_path: str) -> CorpusManifest:
        """
        Load a single corpus manifest.
        """

        return self.manifest_loader.load(manifest_path)

    def ingest(
        self,
        manifest_path: str,
        corpus_path: str,
        source_id: str,
    ) -> Tuple[
        List[CorpusPassage],
        IngestionReport,
        Optional[SourceProvenance],
    ]:
        """
        Ingest a corpus and generate its provenance record.

        Returns:
            passages:
                Successfully loaded corpus passages.

            report:
                Ingestion report.

            provenance:
                Provenance record containing file integrity
                information, or None when the corpus file
                does not exist.
        """

        manifest = self.load_manifest(manifest_path)

        report = IngestionReport(
            corpus_id=manifest.corpus_id
        )

        report.metadata = {
            "title": manifest.title,
            "religion": manifest.religion,
            "tradition": manifest.tradition,
            "source_type": manifest.source_type,
            "languages": manifest.languages,
            "source_id": source_id,
            "manifest_path": str(manifest_path),
            "corpus_path": str(corpus_path),
        }

        loader = CorpusLoader(
            expected_corpus_id=manifest.corpus_id,
            expected_source_id=source_id,
        )

        passages, errors = loader.load_jsonl(corpus_path)

        report.successful_records = len(passages)
        report.failed_records = len(errors)
        report.total_records = (
            report.successful_records
            + report.failed_records
        )
        report.errors.extend(errors)

        provenance = None

        corpus_file = Path(corpus_path)

        if corpus_file.is_file():
            provenance = ProvenanceBuilder.build(
                provenance_id=(
                    f"provenance."
                    f"{manifest.corpus_id}"
                ),
                source_id=source_id,
                title=manifest.title,
                source_type=manifest.source_type,
                corpus_file=corpus_file,
                license=manifest.license,
                copyright_status=manifest.copyright_status,
                original_language=manifest.original_language,
                publication_language=(
                    manifest.languages[0]
                    if manifest.languages
                    else None
                ),
                author=manifest.author,
                translator=manifest.translator,
                publisher=manifest.publisher,
                edition=manifest.edition,
                publication_year=manifest.publication_year,
                source_url=manifest.source_url,
            )

        return passages, report, provenance

    def ingest_from_manifest(
        self,
        manifest_path: str,
        corpus_path: str,
        source_id: str,
    ) -> Tuple[
        List[CorpusPassage],
        IngestionReport,
        Optional[SourceProvenance],
    ]:
        """
        Backward-compatible alias for ingest().
        """

        return self.ingest(
            manifest_path=manifest_path,
            corpus_path=corpus_path,
            source_id=source_id,
        )