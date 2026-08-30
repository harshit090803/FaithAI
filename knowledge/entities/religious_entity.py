from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReligiousEntity:
    """
    Represents a named entity in a religious knowledge system.

    Examples:
        Scripture
        Person
        Deity
        Place
        Practice
        Festival
        Institution
        ReligiousConcept
        Event

    The entity stores provenance so that FaithAI can trace
    knowledge back to its original sources.
    """

    entity_id: str
    name: str
    entity_type: str
    religion: str

    tradition: Optional[str] = None
    description: Optional[str] = None

    aliases: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)

    source_ids: List[str] = field(default_factory=list)

    metadata: Dict[str, str] = field(default_factory=dict)


class ReligiousEntityRegistry:
    """
    Registry containing the religious entities known to FaithAI.

    The registry deliberately does not decide theological truth.
    It stores entities and their source-backed descriptions.
    """

    def __init__(self) -> None:
        self.entities: Dict[str, ReligiousEntity] = {}

    # ---------------------------------------------------------
    # Entity Management
    # ---------------------------------------------------------

    def add_entity(self, entity: ReligiousEntity) -> None:
        """
        Add a new entity to the registry.
        """

        if entity.entity_id in self.entities:
            raise ValueError(
                f"Entity already exists: {entity.entity_id}"
            )

        self.entities[entity.entity_id] = entity

    def update_entity(self, entity: ReligiousEntity) -> None:
        """
        Replace an existing entity.
        """

        if entity.entity_id not in self.entities:
            raise KeyError(
                f"Entity does not exist: {entity.entity_id}"
            )

        self.entities[entity.entity_id] = entity

    def remove_entity(self, entity_id: str) -> None:
        """
        Remove an entity from the registry.
        """

        if entity_id not in self.entities:
            raise KeyError(
                f"Entity does not exist: {entity_id}"
            )

        del self.entities[entity_id]

    def get_entity(
        self,
        entity_id: str,
    ) -> Optional[ReligiousEntity]:
        """
        Retrieve an entity by its unique ID.
        """

        return self.entities.get(entity_id)

    # ---------------------------------------------------------
    # Searching
    # ---------------------------------------------------------

    def find_by_name(
        self,
        name: str,
    ) -> List[ReligiousEntity]:
        """
        Find entities by exact name or alias.
        """

        query = name.strip().lower()

        results = []

        for entity in self.entities.values():

            if entity.name.lower() == query:
                results.append(entity)
                continue

            if any(
                alias.lower() == query
                for alias in entity.aliases
            ):
                results.append(entity)

        return results

    def search(
        self,
        query: str,
    ) -> List[ReligiousEntity]:
        """
        Perform a simple text search across names,
        aliases and descriptions.
        """

        query = query.strip().lower()

        if not query:
            return []

        results = []

        for entity in self.entities.values():

            searchable_text = " ".join(
                [
                    entity.name,
                    entity.description or "",
                    " ".join(entity.aliases),
                ]
            ).lower()

            if query in searchable_text:
                results.append(entity)

        return results

    # ---------------------------------------------------------
    # Filtering
    # ---------------------------------------------------------

    def list_by_religion(
        self,
        religion: str,
    ) -> List[ReligiousEntity]:
        """
        Return all entities belonging to a religion.
        """

        religion = religion.strip().lower()

        return [
            entity
            for entity in self.entities.values()
            if entity.religion.lower() == religion
        ]

    def list_by_type(
        self,
        entity_type: str,
    ) -> List[ReligiousEntity]:
        """
        Return entities of a particular type.

        Examples:
            scripture
            person
            deity
            place
            practice
            festival
        """

        entity_type = entity_type.strip().lower()

        return [
            entity
            for entity in self.entities.values()
            if entity.entity_type.lower() == entity_type
        ]

    def list_by_tradition(
        self,
        tradition: str,
    ) -> List[ReligiousEntity]:
        """
        Return entities belonging to a particular tradition.
        """

        tradition = tradition.strip().lower()

        return [
            entity
            for entity in self.entities.values()
            if entity.tradition
            and entity.tradition.lower() == tradition
        ]

    # ---------------------------------------------------------
    # Source Tracking
    # ---------------------------------------------------------

    def entities_from_source(
        self,
        source_id: str,
    ) -> List[ReligiousEntity]:
        """
        Return entities supported by a particular source.
        """

        return [
            entity
            for entity in self.entities.values()
            if source_id in entity.source_ids
        ]

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self) -> Dict[str, int]:
        """
        Return basic registry statistics.
        """

        return {
            "total_entities": len(self.entities),
        }


# =============================================================
# Test / Demonstration
# =============================================================

if __name__ == "__main__":

    registry = ReligiousEntityRegistry()

    # ---------------------------------------------------------
    # Example 1: Islamic scripture
    # ---------------------------------------------------------

    quran = ReligiousEntity(
        entity_id="islam.scripture.quran",
        name="Qur'an",
        entity_type="scripture",
        religion="islam",
        tradition="islam",
        description=(
            "The central scripture of Islam."
        ),
        aliases=[
            "Quran",
            "Qur'an",
            "القرآن",
        ],
        languages=[
            "Arabic",
            "English",
        ],
        source_ids=[
            "quran_arabic_test",
        ],
    )

    registry.add_entity(quran)

    # ---------------------------------------------------------
    # Example 2: Islamic divine concept
    # ---------------------------------------------------------

    allah = ReligiousEntity(
        entity_id="islam.divine.allah",
        name="Allah",
        entity_type="divine_concept",
        religion="islam",
        tradition="islam",
        description=(
            "The Arabic name for God in Islam."
        ),
        aliases=[
            "Allah",
            "الله",
        ],
        languages=[
            "Arabic",
            "English",
        ],
        source_ids=[
            "quran_arabic_test",
        ],
    )

    registry.add_entity(allah)

    # ---------------------------------------------------------
    # Example 3: Hindu scripture
    # ---------------------------------------------------------

    bhagavad_gita = ReligiousEntity(
        entity_id="hinduism.scripture.bhagavad_gita",
        name="Bhagavad Gita",
        entity_type="scripture",
        religion="hinduism",
        tradition="vaishnavism",
        description=(
            "A Hindu philosophical scripture presented "
            "as a dialogue between Arjuna and Krishna."
        ),
        aliases=[
            "Gita",
            "Bhagavadgita",
            "श्रीमद्भगवद्गीता",
        ],
        languages=[
            "Sanskrit",
            "Hindi",
            "English",
        ],
    )

    registry.add_entity(bhagavad_gita)

    # ---------------------------------------------------------
    # Example 4: Sikh scripture
    # ---------------------------------------------------------

    guru_granth_sahib = ReligiousEntity(
        entity_id="sikhism.scripture.guru_granth_sahib",
        name="Guru Granth Sahib",
        entity_type="scripture",
        religion="sikhism",
        tradition="sikhism",
        description=(
            "The central scripture of Sikhism."
        ),
        aliases=[
            "Sri Guru Granth Sahib",
            "Adi Granth",
        ],
        languages=[
            "Gurmukhi",
            "Punjabi",
            "English",
        ],
    )

    registry.add_entity(guru_granth_sahib)

    # ---------------------------------------------------------
    # Registry statistics
    # ---------------------------------------------------------

    print("=" * 60)
    print("FaithAI Religious Entity Registry")
    print("=" * 60)

    stats = registry.statistics()

    print(
        f"Total entities: "
        f"{stats['total_entities']}"
    )

    # ---------------------------------------------------------
    # Search demonstration
    # ---------------------------------------------------------

    print("\nSearch: Quran")

    results = registry.search("Quran")

    for entity in results:
        print(
            f"- {entity.name} "
            f"[{entity.entity_type}] "
            f"({entity.religion})"
        )

    # ---------------------------------------------------------
    # Religion filtering
    # ---------------------------------------------------------

    print("\nIslamic entities:")

    for entity in registry.list_by_religion("islam"):
        print(
            f"- {entity.name} "
            f"[{entity.entity_type}]"
        )

    # ---------------------------------------------------------
    # Type filtering
    # ---------------------------------------------------------

    print("\nScriptures:")

    for entity in registry.list_by_type("scripture"):
        print(
            f"- {entity.name} "
            f"({entity.religion})"
        )

    # ---------------------------------------------------------
    # Source tracking
    # ---------------------------------------------------------

    print("\nEntities from source quran_arabic_test:")

    for entity in registry.entities_from_source(
        "quran_arabic_test"
    ):
        print(
            f"- {entity.name}"
        )