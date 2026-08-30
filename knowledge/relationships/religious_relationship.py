from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReligiousRelationship:
    """
    Represents an explicit relationship between two
    religious entities or concepts.

    FaithAI does not assume that two concepts are equivalent.
    Relationships must be explicitly defined and, where
    possible, supported by sources.
    """

    relationship_id: str

    source_entity_id: str
    target_entity_id: str

    relationship_type: str

    religion: Optional[str] = None
    tradition: Optional[str] = None

    source_ids: List[str] = field(default_factory=list)

    confidence: Optional[float] = None
    notes: Optional[str] = None

    metadata: Dict[str, str] = field(default_factory=dict)


class ReligiousRelationshipRegistry:
    """
    Registry for relationships between religious entities.

    Examples of relationship types:

        contains
        contains_passage
        associated_with
        taught_by
        written_by
        describes
        mentions
        part_of
        followed_by
        practiced_by
        interpreted_by
        translated_as
        compared_with

    Cross-religious relationships should be represented
    explicitly rather than automatically treated as equivalence.
    """

    def __init__(self) -> None:
        self.relationships: Dict[
            str, ReligiousRelationship
        ] = {}

    # ---------------------------------------------------------
    # Add / Update / Remove
    # ---------------------------------------------------------

    def add_relationship(
        self,
        relationship: ReligiousRelationship,
    ) -> None:
        """
        Add a relationship to the registry.
        """

        if relationship.relationship_id in self.relationships:
            raise ValueError(
                f"Relationship already exists: "
                f"{relationship.relationship_id}"
            )

        self.relationships[
            relationship.relationship_id
        ] = relationship

    def update_relationship(
        self,
        relationship: ReligiousRelationship,
    ) -> None:
        """
        Update an existing relationship.
        """

        if relationship.relationship_id not in self.relationships:
            raise KeyError(
                f"Relationship does not exist: "
                f"{relationship.relationship_id}"
            )

        self.relationships[
            relationship.relationship_id
        ] = relationship

    def remove_relationship(
        self,
        relationship_id: str,
    ) -> None:
        """
        Remove a relationship.
        """

        if relationship_id not in self.relationships:
            raise KeyError(
                f"Relationship does not exist: "
                f"{relationship_id}"
            )

        del self.relationships[relationship_id]

    # ---------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------

    def get_relationship(
        self,
        relationship_id: str,
    ) -> Optional[ReligiousRelationship]:
        """
        Retrieve a relationship by ID.
        """

        return self.relationships.get(
            relationship_id
        )

    # ---------------------------------------------------------
    # Entity-based queries
    # ---------------------------------------------------------

    def relationships_from(
        self,
        entity_id: str,
    ) -> List[ReligiousRelationship]:
        """
        Return relationships originating from an entity.
        """

        return [
            relationship
            for relationship in self.relationships.values()
            if relationship.source_entity_id == entity_id
        ]

    def relationships_to(
        self,
        entity_id: str,
    ) -> List[ReligiousRelationship]:
        """
        Return relationships pointing to an entity.
        """

        return [
            relationship
            for relationship in self.relationships.values()
            if relationship.target_entity_id == entity_id
        ]

    def relationships_for(
        self,
        entity_id: str,
    ) -> List[ReligiousRelationship]:
        """
        Return all relationships involving an entity.
        """

        return [
            relationship
            for relationship in self.relationships.values()
            if (
                relationship.source_entity_id == entity_id
                or relationship.target_entity_id == entity_id
            )
        ]

    # ---------------------------------------------------------
    # Relationship type
    # ---------------------------------------------------------

    def list_by_type(
        self,
        relationship_type: str,
    ) -> List[ReligiousRelationship]:
        """
        Return relationships of a particular type.
        """

        relationship_type = relationship_type.strip().lower()

        return [
            relationship
            for relationship in self.relationships.values()
            if relationship.relationship_type.lower()
            == relationship_type
        ]

    # ---------------------------------------------------------
    # Religion / tradition
    # ---------------------------------------------------------

    def list_by_religion(
        self,
        religion: str,
    ) -> List[ReligiousRelationship]:
        """
        Return relationships associated with a religion.
        """

        religion = religion.strip().lower()

        return [
            relationship
            for relationship in self.relationships.values()
            if relationship.religion
            and relationship.religion.lower() == religion
        ]

    def list_by_tradition(
        self,
        tradition: str,
    ) -> List[ReligiousRelationship]:
        """
        Return relationships associated with a tradition.
        """

        tradition = tradition.strip().lower()

        return [
            relationship
            for relationship in self.relationships.values()
            if relationship.tradition
            and relationship.tradition.lower() == tradition
        ]

    # ---------------------------------------------------------
    # Source tracking
    # ---------------------------------------------------------

    def relationships_from_source(
        self,
        source_id: str,
    ) -> List[ReligiousRelationship]:
        """
        Return relationships supported by a source.
        """

        return [
            relationship
            for relationship in self.relationships.values()
            if source_id in relationship.source_ids
        ]

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self) -> Dict[str, int]:
        """
        Return basic registry statistics.
        """

        return {
            "total_relationships": len(
                self.relationships
            )
        }


# =============================================================
# Test / Demonstration
# =============================================================

if __name__ == "__main__":

    registry = ReligiousRelationshipRegistry()

    # ---------------------------------------------------------
    # Qur'an -> Islam
    # ---------------------------------------------------------

    quran_relationship = ReligiousRelationship(
        relationship_id="islam.quran.part_of.islam",
        source_entity_id="islam.scripture.quran",
        target_entity_id="islam",
        relationship_type="central_scripture_of",
        religion="islam",
        tradition="islam",
        source_ids=[
            "quran_arabic_test"
        ],
        confidence=1.0,
        notes="Demonstration relationship.",
    )

    registry.add_relationship(
        quran_relationship
    )

    # ---------------------------------------------------------
    # Qur'an -> Allah
    # ---------------------------------------------------------

    revelation_relationship = ReligiousRelationship(
        relationship_id="islam.quran.revelation_from.allah",
        source_entity_id="islam.scripture.quran",
        target_entity_id="islam.divine.allah",
        relationship_type="revelation_from",
        religion="islam",
        tradition="islam",
        source_ids=[
            "quran_arabic_test"
        ],
        confidence=1.0,
        notes="Demonstration relationship.",
    )

    registry.add_relationship(
        revelation_relationship
    )

    # ---------------------------------------------------------
    # Example comparative relationship
    # ---------------------------------------------------------

    comparative_relationship = ReligiousRelationship(
        relationship_id=(
            "comparative.allah.brahman.compared_with"
        ),
        source_entity_id="islam.divine.allah",
        target_entity_id="hinduism.concept.brahman",
        relationship_type="compared_with",
        source_ids=[],
        notes=(
            "Comparative relationship only. "
            "Does not assert theological equivalence."
        ),
    )

    registry.add_relationship(
        comparative_relationship
    )

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    print("=" * 60)
    print("FaithAI Religious Relationship Registry")
    print("=" * 60)

    stats = registry.statistics()

    print(
        f"Total relationships: "
        f"{stats['total_relationships']}"
    )

    # ---------------------------------------------------------
    # Query outgoing relationships
    # ---------------------------------------------------------

    print("\nRelationships from Qur'an:")

    for relationship in registry.relationships_from(
        "islam.scripture.quran"
    ):
        print(
            f"- {relationship.relationship_type} "
            f"-> {relationship.target_entity_id}"
        )

    # ---------------------------------------------------------
    # Query by relationship type
    # ---------------------------------------------------------

    print("\nComparative relationships:")

    for relationship in registry.list_by_type(
        "compared_with"
    ):
        print(
            f"- {relationship.source_entity_id} "
            f"↔ {relationship.target_entity_id}"
        )

    # ---------------------------------------------------------
    # Query by religion
    # ---------------------------------------------------------

    print("\nIslamic relationships:")

    for relationship in registry.list_by_religion(
        "islam"
    ):
        print(
            f"- {relationship.source_entity_id} "
            f"--{relationship.relationship_type}--> "
            f"{relationship.target_entity_id}"
        )