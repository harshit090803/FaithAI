import pytest

from knowledge.knowledge_graph import (
    ReligiousKnowledgeGraph,
)

from knowledge.entities.religious_entity import (
    ReligiousEntity,
)

from knowledge.relationships.religious_relationship import (
    ReligiousRelationship,
)

from knowledge.sources.religious_source import (
    ReligiousSource,
)

from knowledge.sources.source_passage import (
    SourcePassage,
)

from knowledge.sources.provenance import (
    SourceProvenance,
)


# ============================================================
# Helpers
# ============================================================


def create_graph():
    return ReligiousKnowledgeGraph()


def create_quran_entity():
    return ReligiousEntity(
        entity_id="islam.scripture.quran",
        name="Qur'an",
        entity_type="scripture",
        religion="islam",
        description="The central scripture of Islam.",
    )


def create_allah_entity():
    return ReligiousEntity(
        entity_id="islam.divine.allah",
        name="Allah",
        entity_type="divine_concept",
        religion="islam",
        description="The Islamic concept of God.",
    )


def create_islam_entity():
    return ReligiousEntity(
        entity_id="islam.religion",
        name="Islam",
        entity_type="religion",
        religion="islam",
        description="The religion of Islam.",
    )


def create_quran_source():
    return ReligiousSource(
        source_id="islam.scripture.quran",
        title="The Qur'an",
        source_type="scripture",
        religion="islam",
        language="Arabic",
        description="Structural Qur'an source.",
    )


def create_quran_passage():
    return SourcePassage(
        passage_id="quran.1.1",
        source_id="islam.scripture.quran",
        reference="Qur'an 1:1",
        text="STRUCTURAL TEST PASSAGE",
        language="Arabic",
    )


def create_quran_provenance():
    return SourceProvenance(
        provenance_id="prov.islam.quran.arabic",
        source_id="islam.scripture.quran",
        title="The Qur'an",
        source_type="scripture",
        original_language="Arabic",
        publication_language="Arabic",
        copyright_status="To be verified",
        verification_status="pending",
        description="Structural provenance record.",
        tags=[
            "islam",
            "quran",
            "arabic",
        ],
    )


# ============================================================
# Entity Tests
# ============================================================


def test_add_entity():
    graph = create_graph()

    entity = create_quran_entity()

    graph.add_entity(entity)

    result = graph.get_entity(
        "islam.scripture.quran"
    )

    assert result is not None
    assert result.name == "Qur'an"


def test_add_duplicate_entity():
    graph = create_graph()

    entity = create_quran_entity()

    graph.add_entity(entity)

    with pytest.raises(ValueError):
        graph.add_entity(entity)


def test_find_entities():
    graph = create_graph()

    quran = create_quran_entity()
    allah = create_allah_entity()

    graph.add_entity(quran)
    graph.add_entity(allah)

    results = graph.search_entities(
        "Qur'an"
    )

    assert len(results) == 1
    assert results[0].entity_id == (
        "islam.scripture.quran"
    )


# ============================================================
# Source Tests
# ============================================================


def test_add_source():
    graph = create_graph()

    source = create_quran_source()

    graph.add_source(source)

    result = graph.get_source(
        "islam.scripture.quran"
    )

    assert result is not None
    assert result.title == "The Qur'an"


def test_add_duplicate_source():
    graph = create_graph()

    source = create_quran_source()

    graph.add_source(source)

    with pytest.raises(ValueError):
        graph.add_source(source)


# ============================================================
# Passage Tests
# ============================================================


def test_add_passage():
    graph = create_graph()

    source = create_quran_source()

    graph.add_source(source)

    passage = create_quran_passage()

    graph.add_passage(passage)

    result = graph.get_passage(
        "quran.1.1"
    )

    assert result is not None
    assert result.reference == "Qur'an 1:1"


def test_passage_requires_existing_source():
    graph = create_graph()

    passage = create_quran_passage()

    with pytest.raises(ValueError):
        graph.add_passage(passage)


def test_passages_for_source():
    graph = create_graph()

    source = create_quran_source()

    graph.add_source(source)

    passage = create_quran_passage()

    graph.add_passage(passage)

    results = graph.passages_for_source(
        "islam.scripture.quran"
    )

    assert len(results) == 1
    assert results[0].passage_id == (
        "quran.1.1"
    )


# ============================================================
# Relationship Tests
# ============================================================


def test_add_relationship():
    graph = create_graph()

    quran = create_quran_entity()
    allah = create_allah_entity()

    source = create_quran_source()

    graph.add_entity(quran)
    graph.add_entity(allah)
    graph.add_source(source)

    relationship = ReligiousRelationship(
        relationship_id="rel.quran.revelation.allah",
        source_entity_id="islam.scripture.quran",
        target_entity_id="islam.divine.allah",
        relationship_type="revelation_from",
        source_ids=[
            "islam.scripture.quran"
        ],
    )

    graph.add_relationship(
        relationship
    )

    results = [
        relationship
        for relationship
        in graph.relationships.relationships.values()
        if relationship.source_entity_id
        == "islam.scripture.quran"
    ]

    assert len(results) == 1

    assert (
        results[0].relationship_type
        == "revelation_from"
    )


def test_relationship_requires_existing_entities():
    graph = create_graph()

    source = create_quran_source()

    graph.add_source(source)

    relationship = ReligiousRelationship(
        relationship_id="rel.invalid",
        source_entity_id="entity.does.not.exist",
        target_entity_id="another.entity",
        relationship_type="related_to",
        source_ids=[
            "islam.scripture.quran"
        ],
    )

    with pytest.raises(ValueError):
        graph.add_relationship(
            relationship
        )


def test_relationship_requires_existing_source():
    graph = create_graph()

    quran = create_quran_entity()
    allah = create_allah_entity()

    graph.add_entity(quran)
    graph.add_entity(allah)

    relationship = ReligiousRelationship(
        relationship_id="rel.invalid.source",
        source_entity_id="islam.scripture.quran",
        target_entity_id="islam.divine.allah",
        relationship_type="revelation_from",
        source_ids=[
            "source.does.not.exist"
        ],
    )

    with pytest.raises(ValueError):
        graph.add_relationship(
            relationship
        )


# ============================================================
# Traversal Tests
# ============================================================


def test_neighbours():
    graph = create_graph()

    quran = create_quran_entity()
    allah = create_allah_entity()

    source = create_quran_source()

    graph.add_entity(quran)
    graph.add_entity(allah)
    graph.add_source(source)

    relationship = ReligiousRelationship(
        relationship_id="rel.quran.allah",
        source_entity_id="islam.scripture.quran",
        target_entity_id="islam.divine.allah",
        relationship_type="revelation_from",
        source_ids=[
            "islam.scripture.quran"
        ],
    )

    graph.add_relationship(
        relationship
    )

    neighbours = graph.neighbors(
        "islam.scripture.quran"
    )

    assert len(neighbours) == 1

    assert (
        neighbours[0].entity_id
        == "islam.divine.allah"
    )


# ============================================================
# Provenance Tests
# ============================================================


def test_add_provenance():
    graph = create_graph()

    source = create_quran_source()

    graph.add_source(source)

    provenance = create_quran_provenance()

    graph.add_provenance(
        provenance
    )

    result = graph.get_provenance(
        "prov.islam.quran.arabic"
    )

    assert result is not None

    assert (
        result.source_id
        == "islam.scripture.quran"
    )


def test_provenance_requires_existing_source():
    graph = create_graph()

    provenance = create_quran_provenance()

    with pytest.raises(ValueError):
        graph.add_provenance(
            provenance
        )


def test_provenance_for_source():
    graph = create_graph()

    source = create_quran_source()

    graph.add_source(source)

    provenance = create_quran_provenance()

    graph.add_provenance(
        provenance
    )

    results = graph.provenance_for_source(
        "islam.scripture.quran"
    )

    assert len(results) == 1

    assert (
        results[0].provenance_id
        == "prov.islam.quran.arabic"
    )


def test_provenance_for_nonexistent_source():
    graph = create_graph()

    with pytest.raises(KeyError):
        graph.provenance_for_source(
            "source.does.not.exist"
        )


# ============================================================
# Statistics Tests
# ============================================================


def test_statistics():
    graph = create_graph()

    quran = create_quran_entity()
    allah = create_allah_entity()
    source = create_quran_source()
    passage = create_quran_passage()
    provenance = create_quran_provenance()

    graph.add_entity(quran)
    graph.add_entity(allah)

    graph.add_source(source)

    graph.add_passage(passage)

    graph.add_provenance(
        provenance
    )

    relationship = ReligiousRelationship(
        relationship_id="rel.quran.allah.stats",
        source_entity_id="islam.scripture.quran",
        target_entity_id="islam.divine.allah",
        relationship_type="revelation_from",
        source_ids=[
            "islam.scripture.quran"
        ],
    )

    graph.add_relationship(
        relationship
    )

    stats = graph.statistics()

    assert stats["entities"] == 2
    assert stats["relationships"] == 1
    assert stats["sources"] == 1
    assert stats["passages"] == 1
    assert stats["provenance"] == 1