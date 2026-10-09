from pathlib import Path

from ingestion.corpus.ingestion_report import IngestionReport
from ingestion.corpus.provenance_builder import ProvenanceBuilder
from ingestion.corpus.quran_reference_validator import (
    QuranReferenceValidator,
)
from ingestion.corpus.quran_validator import (
    QuranStructuralValidator,
)
from ingestion.corpus.tanzil_parser import TanzilParser
from knowledge.knowledge_graph import ReligiousKnowledgeGraph
from knowledge.sources.religious_source import ReligiousSource


QURAN_FILE = Path(
    "data/islam/raw/quran/quran-uthmani.txt"
)


def test_real_quran_corpus_integrity():
    """
    End-to-end integrity test for the real Tanzil corpus.

    Verifies:

    1. The source file exists.
    2. Tanzil text parses successfully.
    3. Structural validation passes.
    4. Reference validation passes.
    5. The expected 6,236 verses are present.
    6. Provenance contains a SHA-256 hash.
    7. Provenance can be registered in the knowledge graph.
    8. The stored hash matches the generated provenance hash.
    """

    assert QURAN_FILE.exists()
    assert QURAN_FILE.is_file()

    # ---------------------------------------------------------
    # 1. Parse the actual Tanzil corpus
    # ---------------------------------------------------------

    parser = TanzilParser()

    passages, parser_errors = parser.parse_file(
        QURAN_FILE
    )

    assert parser_errors == []
    assert len(passages) == 6236

    # ---------------------------------------------------------
    # 2. Structural validation
    # ---------------------------------------------------------

    structural_validator = (
        QuranStructuralValidator()
    )

    structural_errors = (
        structural_validator.validate(passages)
    )

    assert structural_errors == []

    # ---------------------------------------------------------
    # 3. Reference validation
    # ---------------------------------------------------------

    reference_validator = (
        QuranReferenceValidator()
    )

    reference_errors = (
        reference_validator.validate(passages)
    )

    assert reference_errors == []

    # ---------------------------------------------------------
    # 4. Verify first and last passages
    # ---------------------------------------------------------

    assert passages[0].passage_id == "quran.1.1"
    assert passages[0].chapter == 1
    assert passages[0].verse == 1

    assert passages[-1].passage_id == "quran.114.6"
    assert passages[-1].chapter == 114
    assert passages[-1].verse == 6

    # ---------------------------------------------------------
    # 5. Generate provenance
    # ---------------------------------------------------------

    provenance = ProvenanceBuilder.build(
        provenance_id="provenance.islam.quran.arabic",
        source_id="islam.scripture.quran",
        title="Tanzil Quran Text — Uthmani",
        source_type="scripture",
        corpus_file=QURAN_FILE,
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

    assert provenance is not None
    assert provenance.source_id == (
        "islam.scripture.quran"
    )
    assert provenance.file_sha256 is not None
    assert len(provenance.file_sha256) == 64
    assert provenance.is_valid()

    # ---------------------------------------------------------
    # 6. Create the knowledge graph
    # ---------------------------------------------------------

    graph = ReligiousKnowledgeGraph()

    source = ReligiousSource(
        source_id="islam.scripture.quran",
        title="The Qur'an",
        source_type="scripture",
        religion="islam",
    )

    graph.add_source(source)

    # ---------------------------------------------------------
    # 7. Register provenance
    # ---------------------------------------------------------

    graph.add_provenance(provenance)

    stored = graph.get_provenance(
        provenance.provenance_id
    )

    assert stored is not None

    # ---------------------------------------------------------
    # 8. Verify stored provenance integrity
    # ---------------------------------------------------------

    assert (
        stored.file_sha256
        == provenance.file_sha256
    )

    assert stored.source_id == (
        "islam.scripture.quran"
    )

    assert stored.edition == (
        "Uthmani, Version 1.1"
    )

    assert stored.license == (
        "Creative Commons Attribution 3.0"
    )