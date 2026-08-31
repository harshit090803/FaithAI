from typing import Dict, List, Optional

from .religious_source import ReligiousSource


class SourceRegistry:
    """
    Registry containing all sources used by FaithAI.
    """

    def __init__(self) -> None:
        self.sources: Dict[str, ReligiousSource] = {}

    # =========================================================
    # Add / Update / Remove
    # =========================================================

    def add_source(
        self,
        source: ReligiousSource,
    ) -> None:
        """Add a new source."""

        if source.source_id in self.sources:
            raise ValueError(
                f"Source already exists: {source.source_id}"
            )

        self.sources[source.source_id] = source

    def update_source(
        self,
        source: ReligiousSource,
    ) -> None:
        """Update an existing source."""

        if source.source_id not in self.sources:
            raise KeyError(
                f"Source does not exist: {source.source_id}"
            )

        self.sources[source.source_id] = source

    def remove_source(
        self,
        source_id: str,
    ) -> None:
        """Remove a source."""

        if source_id not in self.sources:
            raise KeyError(
                f"Source does not exist: {source_id}"
            )

        del self.sources[source_id]

    # =========================================================
    # Retrieval
    # =========================================================

    def get_source(
        self,
        source_id: str,
    ) -> Optional[ReligiousSource]:
        """Retrieve a source by ID."""

        return self.sources.get(source_id)

    # =========================================================
    # Filtering
    # =========================================================

    def list_by_type(
        self,
        source_type: str,
    ) -> List[ReligiousSource]:
        """Return sources of a particular type."""

        source_type = source_type.strip().lower()

        return [
            source
            for source in self.sources.values()
            if source.source_type.lower() == source_type
        ]

    def list_by_religion(
        self,
        religion: str,
    ) -> List[ReligiousSource]:
        """Return sources associated with a religion."""

        religion = religion.strip().lower()

        return [
            source
            for source in self.sources.values()
            if source.religion
            and source.religion.lower() == religion
        ]

    def list_by_language(
        self,
        language: str,
    ) -> List[ReligiousSource]:
        """Return sources available in a language."""

        language = language.strip().lower()

        return [
            source
            for source in self.sources.values()
            if source.language
            and source.language.lower() == language
        ]

    # =========================================================
    # Statistics
    # =========================================================

    def statistics(self) -> Dict[str, int]:
        """Return basic source statistics."""

        return {
            "total_sources": len(self.sources)
        }


# =============================================================
# Demonstration
# =============================================================

if __name__ == "__main__":

    registry = SourceRegistry()

    quran = ReligiousSource(
        source_id="islam.scripture.quran",
        title="The Qur'an",
        source_type="scripture",
        religion="islam",
        tradition="islam",
        language="Arabic",
        copyright_status="Source text status to be verified",
        description=(
            "Primary Islamic scripture represented "
            "as a source record."
        ),
        tags=[
            "quran",
            "scripture",
            "islam",
        ],
    )

    registry.add_source(quran)

    english_translation = ReligiousSource(
        source_id="islam.translation.example_english",
        title="Example English Translation",
        source_type="translation",
        religion="islam",
        tradition="islam",
        language="English",
        translator="To be specified",
        copyright_status="To be verified",
        description=(
            "Placeholder translation record. "
            "Do not populate with copyrighted text "
            "until redistribution rights are verified."
        ),
        tags=[
            "quran",
            "translation",
            "english",
        ],
    )

    registry.add_source(english_translation)

    print("=" * 60)
    print("FaithAI Source Registry")
    print("=" * 60)

    stats = registry.statistics()

    print(
        f"Total sources: "
        f"{stats['total_sources']}"
    )

    print("\nAll sources:")

    for source in registry.sources.values():
        print(
            f"- {source.title}"
            f" [{source.source_type}]"
            f" ({source.source_id})"
        )

    print("\nIslamic sources:")

    for source in registry.list_by_religion("islam"):
        print(
            f"- {source.title}"
            f" [{source.language}]"
        )

    print("\nScriptures:")

    for source in registry.list_by_type("scripture"):
        print(
            f"- {source.title}"
        )