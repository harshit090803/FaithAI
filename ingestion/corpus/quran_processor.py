import json
from pathlib import Path
from typing import List

from ingestion.corpus.provenance_builder import ProvenanceBuilder
from ingestion.corpus.quran_reference_validator import (
    QuranReferenceValidator,
)
from ingestion.corpus.quran_validator import (
    QuranStructuralValidator,
)
from ingestion.corpus.tanzil_parser import TanzilParser
from knowledge.sources.corpus_passage import CorpusPassage


class QuranCorpusProcessor:
    """
    Converts the validated raw Tanzil Qur'an corpus into
    FaithAI's canonical processed representation.

    The original Arabic verse text is preserved exactly.
    """

    def __init__(
        self,
        raw_path: str | Path,
        output_dir: str | Path,
    ):
        self.raw_path = Path(raw_path)
        self.output_dir = Path(output_dir)

    def process(self) -> List[CorpusPassage]:
        """
        Parse, validate, and write the canonical corpus.
        """

        if not self.raw_path.exists():
            raise FileNotFoundError(
                f"Raw corpus does not exist: {self.raw_path}"
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ---------------------------------------------------------
        # 1. Parse
        # ---------------------------------------------------------

        parser = TanzilParser()

        passages, parser_errors = parser.parse_file(
            self.raw_path
        )

        if parser_errors:
            raise ValueError(
                "Parser validation failed:\n"
                + "\n".join(parser_errors)
            )

        # ---------------------------------------------------------
        # 2. Structural validation
        # ---------------------------------------------------------

        structural_validator = (
            QuranStructuralValidator()
        )

        structural_errors = (
            structural_validator.validate(passages)
        )

        if structural_errors:
            raise ValueError(
                "Structural validation failed:\n"
                + "\n".join(structural_errors)
            )

        # ---------------------------------------------------------
        # 3. Reference validation
        # ---------------------------------------------------------

        reference_validator = (
            QuranReferenceValidator()
        )

        reference_errors = (
            reference_validator.validate(passages)
        )

        if reference_errors:
            raise ValueError(
                "Reference validation failed:\n"
                + "\n".join(reference_errors)
            )

        # ---------------------------------------------------------
        # 4. Generate provenance
        # ---------------------------------------------------------

        provenance = ProvenanceBuilder.build(
            provenance_id="provenance.islam.quran.arabic",
            source_id="islam.scripture.quran",
            title="Tanzil Quran Text — Uthmani",
            source_type="scripture",
            corpus_file=self.raw_path,
            license="Creative Commons Attribution 3.0",
            copyright_status=(
                "Tanzil copyright notice and attribution "
                "required; text modification not permitted."
            ),
            original_language="Arabic",
            publication_language="Arabic",
            publisher="Tanzil Project",
            edition="Uthmani, Version 1.1",
            publication_year=2021,
            source_url="https://tanzil.net/",
        )

        if not provenance.is_valid():
            raise ValueError(
                "Generated provenance is invalid."
            )

        # ---------------------------------------------------------
        # 5. Write canonical passages
        # ---------------------------------------------------------

        passages_path = (
            self.output_dir / "passages.jsonl"
        )

        with passages_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            for passage in passages:
                json.dump(
                    passage.to_dict(),
                    file,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                file.write("\n")

        # ---------------------------------------------------------
        # 6. Write provenance
        # ---------------------------------------------------------

        provenance_path = (
            self.output_dir / "provenance.json"
        )

        with provenance_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                provenance.to_dict(),
                file,
                ensure_ascii=False,
                indent=4,
            )

        # ---------------------------------------------------------
        # 7. Write corpus manifest
        # ---------------------------------------------------------

        manifest = {
            "corpus_id": "islam.quran.arabic",
            "title": "Tanzil Quran Text — Uthmani",
            "religion": "islam",
            "tradition": "islam",
            "source_type": "scripture",
            "original_language": "Arabic",
            "language": "Arabic",
            "publisher": "Tanzil Project",
            "edition": "Uthmani, Version 1.1",
            "publication_year": 2021,
            "source_id": "islam.scripture.quran",
            "license": "Creative Commons Attribution 3.0",
            "copyright_status": (
                "Tanzil copyright notice and attribution "
                "required; text modification not permitted."
            ),
            "source_url": "https://tanzil.net/",
            "raw_file": str(self.raw_path),
            "raw_sha256": provenance.file_sha256,
            "passage_count": len(passages),
            "surah_count": 114,
            "processed_format": "JSONL",
        }

        manifest_path = (
            self.output_dir / "manifest.json"
        )

        with manifest_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                manifest,
                file,
                ensure_ascii=False,
                indent=4,
            )

        # ---------------------------------------------------------
        # 8. Write validation report
        # ---------------------------------------------------------

        structural_statistics = (
            structural_validator.statistics(
                passages
            )
        )

        reference_statistics = (
            reference_validator.statistics(
                passages
            )
        )

        validation_report = {
            "status": "passed",
            "parser_errors": 0,
            "structural_errors": 0,
            "reference_errors": 0,
            "passage_count": len(passages),
            "structural_statistics": (
                structural_statistics
            ),
            "reference_statistics": (
                reference_statistics
            ),
            "raw_sha256": provenance.file_sha256,
        }

        report_path = (
            self.output_dir / "validation_report.json"
        )

        with report_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                validation_report,
                file,
                ensure_ascii=False,
                indent=4,
            )

        return passages


if __name__ == "__main__":
    processor = QuranCorpusProcessor(
        raw_path=(
            "data/islam/raw/quran/"
            "quran-uthmani.txt"
        ),
        output_dir=(
            "data/islam/processed/quran"
        ),
    )

    passages = processor.process()

    print("Quran corpus processing")
    print("-----------------------")
    print("Status   : PASSED")
    print("Passages :", len(passages))
    print()
    print("Generated:")
    print(" - data/islam/processed/quran/passages.jsonl")
    print(" - data/islam/processed/quran/provenance.json")
    print(" - data/islam/processed/quran/manifest.json")
    print(" - data/islam/processed/quran/validation_report.json")