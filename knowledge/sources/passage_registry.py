from typing import Dict, List, Optional

from .source_passage import SourcePassage


class PassageRegistry:
    """
    Registry for textual passages used by FaithAI.
    """

    def __init__(self) -> None:
        self.passages: Dict[str, SourcePassage] = {}

    # =========================================================
    # Add
    # =========================================================

    def add_passage(
        self,
        passage: SourcePassage,
    ) -> None:
        """Add a passage to the registry."""

        if passage.passage_id in self.passages:
            raise ValueError(
                f"Passage already exists: "
                f"{passage.passage_id}"
            )

        self.passages[
            passage.passage_id
        ] = passage

    # =========================================================
    # Update
    # =========================================================

    def update_passage(
        self,
        passage: SourcePassage,
    ) -> None:
        """Update an existing passage."""

        if passage.passage_id not in self.passages:
            raise KeyError(
                f"Passage does not exist: "
                f"{passage.passage_id}"
            )

        self.passages[
            passage.passage_id
        ] = passage

    # =========================================================
    # Remove
    # =========================================================

    def remove_passage(
        self,
        passage_id: str,
    ) -> None:
        """Remove a passage."""

        if passage_id not in self.passages:
            raise KeyError(
                f"Passage does not exist: "
                f"{passage_id}"
            )

        del self.passages[passage_id]

    # =========================================================
    # Retrieve
    # =========================================================

    def get_passage(
        self,
        passage_id: str,
    ) -> Optional[SourcePassage]:
        """Retrieve a passage by ID."""

        return self.passages.get(
            passage_id
        )

    # =========================================================
    # Source Filtering
    # =========================================================

    def list_by_source(
        self,
        source_id: str,
    ) -> List[SourcePassage]:
        """Return all passages belonging to a source."""

        return [
            passage
            for passage in self.passages.values()
            if passage.source_id == source_id
        ]

    # =========================================================
    # Language Filtering
    # =========================================================

    def list_by_language(
        self,
        language: str,
    ) -> List[SourcePassage]:
        """Return passages in a particular language."""

        language = language.strip().lower()

        return [
            passage
            for passage in self.passages.values()
            if passage.language.lower()
            == language
        ]

    # =========================================================
    # Search
    # =========================================================

    def search(
        self,
        query: str,
    ) -> List[SourcePassage]:
        """
        Simple text search.

        This is intentionally basic.
        Semantic/vector search will be implemented later.
        """

        query = query.strip().lower()

        if not query:
            return []

        results = []

        for passage in self.passages.values():

            searchable_text = (
                passage.text.lower()
            )

            if passage.reference:
                searchable_text += (
                    " "
                    + passage.reference.lower()
                )

            if query in searchable_text:
                results.append(
                    passage
                )

        return results

    # =========================================================
    # Statistics
    # =========================================================

    def statistics(self) -> Dict[str, int]:
        """Return registry statistics."""

        return {
            "total_passages": len(
                self.passages
            )
        }


# =============================================================
# Demonstration
# =============================================================

if __name__ == "__main__":

    registry = PassageRegistry()

    # ---------------------------------------------------------
    # IMPORTANT:
    # This is a STRUCTURAL test passage.
    # It is not being presented as an actual scripture quote.
    # ---------------------------------------------------------

    passage = SourcePassage(
        passage_id="test.islam.quran.001",
        source_id="islam.scripture.quran",
        text=(
            "STRUCTURAL TEST PASSAGE"
        ),
        language="English",
        reference="Test Reference 1",
        book="Test Book",
        chapter="1",
        verse="1",
        metadata={
            "test": "true"
        },
        tags=[
            "test",
            "example"
        ],
    )

    registry.add_passage(
        passage
    )

    print("=" * 60)
    print("FaithAI Passage Registry")
    print("=" * 60)

    stats = registry.statistics()

    print(
        f"Total passages: "
        f"{stats['total_passages']}"
    )

    print("\nPassages:")

    for item in registry.passages.values():

        print(
            f"- {item.passage_id}"
        )

        print(
            f"  Source: {item.source_id}"
        )

        print(
            f"  Reference: {item.reference}"
        )

        print(
            f"  Language: {item.language}"
        )

    print("\nSearch test:")

    results = registry.search(
        "STRUCTURAL TEST"
    )

    for item in results:

        print(
            f"- Found: {item.passage_id}"
        )

    print("\nPassage registry test completed.")