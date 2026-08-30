from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Concept:
    """
    A normalized religious concept.

    Examples:
        Allah
        Brahman
        Waheguru
        Trinity
        Karma
        Nirvana
        Torah
    """

    concept_id: str
    name: str
    religion: str

    tradition: Optional[str] = None
    description: Optional[str] = None

    aliases: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)

    source_ids: List[str] = field(default_factory=list)


@dataclass
class ConceptRelation:
    """
    Represents a relationship between two religious concepts.

    Example:
        concept_a -> concept_b

    The relationship itself is explicitly named so that
    FaithAI does not silently infer theological equivalence.
    """

    relation_id: str

    source_concept_id: str
    target_concept_id: str

    relation_type: str

    religion: Optional[str] = None
    tradition: Optional[str] = None

    source_ids: List[str] = field(default_factory=list)

    confidence: Optional[float] = None

    notes: Optional[str] = None


class ReligiousOntology:
    """
    Registry for FaithAI's normalized religious concepts
    and explicitly defined relationships.

    Important:
        The ontology stores relationships as data.
        It does NOT assume that concepts from different
        religions are equivalent merely because they appear
        similar.
    """

    def __init__(self) -> None:
        self.concepts: Dict[str, Concept] = {}
        self.relations: Dict[str, ConceptRelation] = {}

    # ---------------------------------------------------------
    # Concepts
    # ---------------------------------------------------------

    def add_concept(self, concept: Concept) -> None:
        if concept.concept_id in self.concepts:
            raise ValueError(
                f"Concept already exists: {concept.concept_id}"
            )

        self.concepts[concept.concept_id] = concept

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        return self.concepts.get(concept_id)

    def list_concepts(
        self,
        religion: Optional[str] = None,
    ) -> List[Concept]:

        concepts = list(self.concepts.values())

        if religion is not None:
            concepts = [
                concept
                for concept in concepts
                if concept.religion.lower() == religion.lower()
            ]

        return concepts

    # ---------------------------------------------------------
    # Relations
    # ---------------------------------------------------------

    def add_relation(self, relation: ConceptRelation) -> None:
        if relation.relation_id in self.relations:
            raise ValueError(
                f"Relation already exists: {relation.relation_id}"
            )

        if relation.source_concept_id not in self.concepts:
            raise ValueError(
                f"Source concept does not exist: "
                f"{relation.source_concept_id}"
            )

        if relation.target_concept_id not in self.concepts:
            raise ValueError(
                f"Target concept does not exist: "
                f"{relation.target_concept_id}"
            )

        self.relations[relation.relation_id] = relation

    def get_relation(
        self,
        relation_id: str,
    ) -> Optional[ConceptRelation]:

        return self.relations.get(relation_id)

    def list_relations(
        self,
        religion: Optional[str] = None,
    ) -> List[ConceptRelation]:

        relations = list(self.relations.values())

        if religion is not None:
            relations = [
                relation
                for relation in relations
                if relation.religion
                and relation.religion.lower() == religion.lower()
            ]

        return relations

    # ---------------------------------------------------------
    # Relationship traversal
    # ---------------------------------------------------------

    def related_concepts(
        self,
        concept_id: str,
    ) -> List[Concept]:

        related_ids = set()

        for relation in self.relations.values():

            if relation.source_concept_id == concept_id:
                related_ids.add(relation.target_concept_id)

            elif relation.target_concept_id == concept_id:
                related_ids.add(relation.source_concept_id)

        return [
            self.concepts[related_id]
            for related_id in related_ids
            if related_id in self.concepts
        ]

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self) -> Dict[str, int]:
        return {
            "concepts": len(self.concepts),
            "relations": len(self.relations),
        }


if __name__ == "__main__":

    ontology = ReligiousOntology()

    # ---------------------------------------------------------
    # Example concepts
    # ---------------------------------------------------------

    allah = Concept(
        concept_id="islam.allah",
        name="Allah",
        religion="islam",
        tradition="islam",
        description="The Arabic name for God in Islam.",
        aliases=["Allah"],
        languages=["Arabic", "English"],
    )

    quran = Concept(
        concept_id="islam.quran",
        name="Qur'an",
        religion="islam",
        tradition="islam",
        description="The central scripture of Islam.",
        aliases=["Quran", "Qur'an", "القرآن"],
        languages=["Arabic", "English"],
    )

    ontology.add_concept(allah)
    ontology.add_concept(quran)

    # ---------------------------------------------------------
    # Example relationship
    # ---------------------------------------------------------

    relation = ConceptRelation(
        relation_id="islam.quran.primary_scripture",
        source_concept_id="islam.quran",
        target_concept_id="islam.allah",
        relation_type="revelation_from",
        religion="islam",
        tradition="islam",
        notes="Example ontology relationship for testing only.",
    )

    ontology.add_relation(relation)

    # ---------------------------------------------------------
    # Output
    # ---------------------------------------------------------

    print("FaithAI Religious Ontology")
    print("=" * 50)

    stats = ontology.statistics()

    print(f"Concepts  : {stats['concepts']}")
    print(f"Relations : {stats['relations']}")

    print("\nRelated concepts of islam.quran:")

    for concept in ontology.related_concepts("islam.quran"):
        print(
            f"- {concept.name} "
            f"({concept.concept_id})"
        )