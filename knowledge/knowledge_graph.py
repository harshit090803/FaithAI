from typing import Dict, List, Optional

from .entities.religious_entity import (
    ReligiousEntity,
    ReligiousEntityRegistry,
)

from .relationships.religious_relationship import (
    ReligiousRelationship,
    ReligiousRelationshipRegistry,
)

from .sources.religious_source import ReligiousSource
from .sources.source_registry import SourceRegistry

from .sources.source_passage import SourcePassage
from .sources.passage_registry import PassageRegistry


class ReligiousKnowledgeGraph:
    """
    Central knowledge graph for FaithAI.

    Architecture:

        Entities
            |
        Relationships
            |
        Sources
            |
        Passages

    The graph stores structured, source-backed information.
    It does not independently determine theological truth.
    """

    def __init__(self) -> None:

        self.entities = ReligiousEntityRegistry()

        self.relationships = (
            ReligiousRelationshipRegistry()
        )

        self.sources = SourceRegistry()

        self.passages = PassageRegistry()

    # =========================================================
    # ENTITY OPERATIONS
    # =========================================================

    def add_entity(
        self,
        entity: ReligiousEntity,
    ) -> None:
        """Add an entity."""

        self.entities.add_entity(entity)

    def get_entity(
        self,
        entity_id: str,
    ) -> Optional[ReligiousEntity]:
        """Retrieve an entity."""

        return self.entities.get_entity(
            entity_id
        )

    # =========================================================
    # SOURCE OPERATIONS
    # =========================================================

    def add_source(
        self,
        source: ReligiousSource,
    ) -> None:
        """Add a source."""

        self.sources.add_source(source)

    def get_source(
        self,
        source_id: str,
    ) -> Optional[ReligiousSource]:
        """Retrieve a source."""

        return self.sources.get_source(
            source_id
        )

    # =========================================================
    # PASSAGE OPERATIONS
    # =========================================================

    def add_passage(
        self,
        passage: SourcePassage,
    ) -> None:
        """
        Add a passage after verifying that its source exists.
        """

        source = self.get_source(
            passage.source_id
        )

        if source is None:
            raise ValueError(
                "Passage references a "
                "non-existent source: "
                f"{passage.source_id}"
            )

        self.passages.add_passage(
            passage
        )

    def get_passage(
        self,
        passage_id: str,
    ) -> Optional[SourcePassage]:
        """Retrieve a passage."""

        return self.passages.get_passage(
            passage_id
        )

    def passages_for_source(
        self,
        source_id: str,
    ) -> List[SourcePassage]:
        """
        Return all passages belonging to a source.
        """

        if self.get_source(source_id) is None:
            raise KeyError(
                "Source does not exist: "
                f"{source_id}"
            )

        return self.passages.list_by_source(
            source_id
        )

    # =========================================================
    # RELATIONSHIP OPERATIONS
    # =========================================================

    def add_relationship(
        self,
        relationship: ReligiousRelationship,
    ) -> None:
        """
        Add a relationship after validating:

        1. Source entity exists.
        2. Target entity exists.
        3. Every referenced source exists.
        """

        source_entity = self.get_entity(
            relationship.source_entity_id
        )

        if source_entity is None:
            raise ValueError(
                "Source entity does not exist: "
                f"{relationship.source_entity_id}"
            )

        target_entity = self.get_entity(
            relationship.target_entity_id
        )

        if target_entity is None:
            raise ValueError(
                "Target entity does not exist: "
                f"{relationship.target_entity_id}"
            )

        missing_sources = []

        for source_id in relationship.source_ids:

            if self.get_source(source_id) is None:
                missing_sources.append(source_id)

        if missing_sources:

            raise ValueError(
                "Relationship references "
                "non-existent sources: "
                f"{missing_sources}"
            )

        self.relationships.add_relationship(
            relationship
        )

    # =========================================================
    # RELATIONSHIP TRAVERSAL
    # =========================================================

    def outgoing(
        self,
        entity_id: str,
    ) -> List[ReligiousRelationship]:

        return self.relationships.relationships_from(
            entity_id
        )

    def incoming(
        self,
        entity_id: str,
    ) -> List[ReligiousRelationship]:

        return self.relationships.relationships_to(
            entity_id
        )

    def connections(
        self,
        entity_id: str,
    ) -> List[ReligiousRelationship]:

        return self.relationships.relationships_for(
            entity_id
        )

    # =========================================================
    # NEIGHBOURS
    # =========================================================

    def neighbors(
        self,
        entity_id: str,
    ) -> List[ReligiousEntity]:

        relationships = self.connections(
            entity_id
        )

        result = []

        for relationship in relationships:

            if (
                relationship.source_entity_id
                == entity_id
            ):

                target = self.get_entity(
                    relationship.target_entity_id
                )

                if target is not None:
                    result.append(target)

            else:

                source = self.get_entity(
                    relationship.source_entity_id
                )

                if source is not None:
                    result.append(source)

        return result

    # =========================================================
    # SEARCH
    # =========================================================

    def search_entities(
        self,
        query: str,
    ) -> List[ReligiousEntity]:

        return self.entities.search(query)

    def search_passages(
        self,
        query: str,
    ) -> List[SourcePassage]:

        return self.passages.search(query)

    # =========================================================
    # RELIGION FILTERING
    # =========================================================

    def entities_by_religion(
        self,
        religion: str,
    ) -> List[ReligiousEntity]:

        return self.entities.list_by_religion(
            religion
        )

    def relationships_by_religion(
        self,
        religion: str,
    ) -> List[ReligiousRelationship]:

        return self.relationships.list_by_religion(
            religion
        )

    def sources_by_religion(
        self,
        religion: str,
    ) -> List[ReligiousSource]:

        return self.sources.list_by_religion(
            religion
        )

    # =========================================================
    # SOURCE-BACKED RELATIONSHIPS
    # =========================================================

    def sources_for_relationship(
        self,
        relationship_id: str,
    ) -> List[ReligiousSource]:
        """
        Return the actual sources referenced by a relationship.
        """

        relationship = (
            self.relationships.get_relationship(
                relationship_id
            )
        )

        if relationship is None:
            raise KeyError(
                "Relationship does not exist: "
                f"{relationship_id}"
            )

        result = []

        for source_id in relationship.source_ids:

            source = self.get_source(
                source_id
            )

            if source is not None:
                result.append(source)

        return result

    # =========================================================
    # STATISTICS
    # =========================================================

    def statistics(self) -> Dict[str, int]:

        return {
            "entities": len(
                self.entities.entities
            ),
            "relationships": len(
                self.relationships.relationships
            ),
            "sources": len(
                self.sources.sources
            ),
            "passages": len(
                self.passages.passages
            ),
        }


# =============================================================
# DEMONSTRATION / INTEGRATION TEST
# =============================================================

if __name__ == "__main__":

    graph = ReligiousKnowledgeGraph()

    # =========================================================
    # SOURCE
    # =========================================================

    quran_source = ReligiousSource(
        source_id="islam.scripture.quran",
        title="The Qur'an",
        source_type="scripture",
        religion="islam",
        tradition="islam",
        language="Arabic",
        copyright_status=(
            "Source text status to be verified"
        ),
    )

    graph.add_source(
        quran_source
    )

    # =========================================================
    # PASSAGE
    # =========================================================

    test_passage = SourcePassage(
        passage_id="test.islam.quran.001",
        source_id="islam.scripture.quran",
        text="STRUCTURAL TEST PASSAGE",
        language="Arabic",
        reference="Test Reference 1",
        chapter="1",
        verse="1",
        metadata={
            "test": "true"
        },
        tags=[
            "test"
        ],
    )

    graph.add_passage(
        test_passage
    )

    # =========================================================
    # ENTITIES
    # =========================================================

    islam = ReligiousEntity(
        entity_id="islam.religion",
        name="Islam",
        entity_type="religion",
        religion="islam",
        tradition="islam",
    )

    quran = ReligiousEntity(
        entity_id="islam.scripture.quran",
        name="Qur'an",
        entity_type="scripture",
        religion="islam",
        tradition="islam",
    )

    allah = ReligiousEntity(
        entity_id="islam.divine.allah",
        name="Allah",
        entity_type="divine_concept",
        religion="islam",
        tradition="islam",
    )

    graph.add_entity(islam)
    graph.add_entity(quran)
    graph.add_entity(allah)

    # =========================================================
    # RELATIONSHIP
    # =========================================================

    graph.add_relationship(
        ReligiousRelationship(
            relationship_id=(
                "islam.quran.revelation_from.allah"
            ),
            source_entity_id=(
                "islam.scripture.quran"
            ),
            target_entity_id=(
                "islam.divine.allah"
            ),
            relationship_type="revelation_from",
            religion="islam",
            source_ids=[
                "islam.scripture.quran"
            ],
        )
    )

    # =========================================================
    # STATISTICS
    # =========================================================

    print("=" * 60)
    print(
        "FaithAI Integrated Knowledge Graph"
    )
    print("=" * 60)

    stats = graph.statistics()

    print(
        f"Entities       : {stats['entities']}"
    )

    print(
        f"Relationships   : {stats['relationships']}"
    )

    print(
        f"Sources         : {stats['sources']}"
    )

    print(
        f"Passages        : {stats['passages']}"
    )

    # =========================================================
    # PASSAGES FOR SOURCE
    # =========================================================

    print("\nPassages belonging to Qur'an:")

    passages = graph.passages_for_source(
        "islam.scripture.quran"
    )

    for passage in passages:

        print(
            f"- {passage.passage_id}"
        )

        print(
            f"  Reference: "
            f"{passage.reference}"
        )

        print(
            f"  Text: "
            f"{passage.text}"
        )

    # =========================================================
    # RELATIONSHIP
    # =========================================================

    print("\nQur'an relationships:")

    for relationship in graph.outgoing(
        "islam.scripture.quran"
    ):

        target = graph.get_entity(
            relationship.target_entity_id
        )

        if target:

            print(
                f"- {relationship.relationship_type}"
                f" -> {target.name}"
            )

    # =========================================================
    # SOURCES
    # =========================================================

    print(
        "\nSources for revelation relationship:"
    )

    sources = graph.sources_for_relationship(
        "islam.quran.revelation_from.allah"
    )

    for source in sources:

        print(
            f"- {source.title}"
            f" [{source.source_type}]"
        )

    # =========================================================
    # INVALID PASSAGE TEST
    # =========================================================

    print(
        "\nTesting invalid passage source..."
    )

    try:

        graph.add_passage(
            SourcePassage(
                passage_id="invalid.passage",
                source_id="source.does.not.exist",
                text="INVALID TEST",
                language="English",
            )
        )

    except ValueError as error:

        print(
            f"✓ Correctly rejected: {error}"
        )

    print(
        "\nKnowledge graph integration test completed."
    )