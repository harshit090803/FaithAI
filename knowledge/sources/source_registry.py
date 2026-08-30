import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SourceRecord:
    """
    Describes the origin and provenance of a religious source.

    This metadata is kept separate from the actual religious text.
    """

    source_id: str
    religion: str
    tradition: str

    title: str
    book: Optional[str] = None

    language: Optional[str] = None
    original_language: Optional[str] = None

    author: Optional[str] = None
    translator: Optional[str] = None

    edition: Optional[str] = None
    publication: Optional[str] = None

    source_url: Optional[str] = None

    source_type: str = "primary_source"

    copyright_status: Optional[str] = None
    license: Optional[str] = None

    provenance: Optional[str] = None

    notes: Optional[str] = None


class SourceRegistry:
    """
    Registry for all FaithAI religious sources.

    Example:

        registry = SourceRegistry(
            "data/islam/source_registry.json"
        )

        registry.add_source(
            SourceRecord(...)
        )

        registry.save()
    """

    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.sources: dict[str, SourceRecord] = {}

        if self.registry_path.exists():
            self.load()

    def add_source(self, source: SourceRecord) -> None:
        """
        Add a source to the registry.

        Raises:
            ValueError: if source_id already exists.
        """

        if source.source_id in self.sources:
            raise ValueError(
                f"Source already exists: "
                f"{source.source_id}"
            )

        self.sources[source.source_id] = source

    def update_source(self, source: SourceRecord) -> None:
        """
        Update an existing source.
        """

        if source.source_id not in self.sources:
            raise KeyError(
                f"Source not found: "
                f"{source.source_id}"
            )

        self.sources[source.source_id] = source

    def get_source(
        self,
        source_id: str
    ) -> SourceRecord:
        """
        Retrieve a source by source_id.
        """

        if source_id not in self.sources:
            raise KeyError(
                f"Source not found: {source_id}"
            )

        return self.sources[source_id]

    def remove_source(
        self,
        source_id: str
    ) -> None:
        """
        Remove a source from the registry.
        """

        if source_id not in self.sources:
            raise KeyError(
                f"Source not found: {source_id}"
            )

        del self.sources[source_id]

    def list_sources(self) -> list[SourceRecord]:
        """
        Return all registered sources.
        """

        return list(self.sources.values())

    def save(self) -> None:
        """
        Save registry to JSON.
        """

        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "version": "1.0.0",
            "sources": [
                asdict(source)
                for source in self.sources.values()
            ]
        }

        with self.registry_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )

    def load(self) -> None:
        """
        Load registry from JSON.
        """

        with self.registry_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.sources.clear()

        for item in data.get("sources", []):

            source = SourceRecord(**item)

            self.sources[source.source_id] = source


if __name__ == "__main__":

    registry = SourceRegistry(
        "data/islam/source_registry.json"
    )

    test_source = SourceRecord(
        source_id="quran_arabic_test",
        religion="islam",
        tradition="islam",
        title="Qur'an",
        book="Qur'an",
        language="Arabic",
        original_language="Arabic",
        source_type="primary_source",
        copyright_status="test",
        provenance="FaithAI test source",
    )

    if test_source.source_id not in registry.sources:
        registry.add_source(test_source)

    registry.save()

    print("Source registry created successfully.")
    print(
        f"Registered sources: "
        f"{len(registry.list_sources())}"
    )