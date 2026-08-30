from .religious_entity import (
    ReligiousEntity,
    ReligiousEntityRegistry,
)


def build_islamic_registry() -> ReligiousEntityRegistry:
    """
    Create the initial Islamic entity registry.

    These are structural seed entities only.
    Detailed theological claims should be supported by
    source passages added later.
    """

    registry = ReligiousEntityRegistry()

    entities = [

        ReligiousEntity(
            entity_id="islam.religion",
            name="Islam",
            entity_type="religion",
            religion="islam",
            tradition="islam",
            description="Islamic religious tradition.",
        ),

        ReligiousEntity(
            entity_id="islam.divine.allah",
            name="Allah",
            entity_type="divine_concept",
            religion="islam",
            tradition="islam",
            aliases=[
                "Allah",
                "الله",
            ],
            languages=[
                "Arabic",
                "English",
            ],
        ),

        ReligiousEntity(
            entity_id="islam.scripture.quran",
            name="Qur'an",
            entity_type="scripture",
            religion="islam",
            tradition="islam",
            aliases=[
                "Quran",
                "Qur'an",
                "القرآن",
            ],
            languages=[
                "Arabic",
                "English",
            ],
        ),

        ReligiousEntity(
            entity_id="islam.person.muhammad",
            name="Muhammad",
            entity_type="person",
            religion="islam",
            tradition="islam",
            aliases=[
                "Muhammad",
                "Muhammad ibn Abdullah",
            ],
        ),

        ReligiousEntity(
            entity_id="islam.concept.tawhid",
            name="Tawhid",
            entity_type="religious_concept",
            religion="islam",
            tradition="islam",
            aliases=[
                "Tawhid",
                "Tawheed",
            ],
        ),

        ReligiousEntity(
            entity_id="islam.practice.salah",
            name="Salah",
            entity_type="practice",
            religion="islam",
            tradition="islam",
            aliases=[
                "Salat",
                "Salah",
                "Prayer",
            ],
        ),

        ReligiousEntity(
            entity_id="islam.practice.zakat",
            name="Zakat",
            entity_type="practice",
            religion="islam",
            tradition="islam",
        ),

        ReligiousEntity(
            entity_id="islam.practice.sawm",
            name="Sawm",
            entity_type="practice",
            religion="islam",
            tradition="islam",
            aliases=[
                "Fasting",
                "Sawm",
            ],
        ),

        ReligiousEntity(
            entity_id="islam.practice.hajj",
            name="Hajj",
            entity_type="practice",
            religion="islam",
            tradition="islam",
        ),

        ReligiousEntity(
            entity_id="islam.concept.akhirah",
            name="Akhirah",
            entity_type="religious_concept",
            religion="islam",
            tradition="islam",
            aliases=[
                "Hereafter",
                "Akhirah",
            ],
        ),

        ReligiousEntity(
            entity_id="islam.concept.revelation",
            name="Revelation",
            entity_type="religious_concept",
            religion="islam",
            tradition="islam",
            aliases=[
                "Wahy",
                "Wahi",
            ],
        ),
    ]

    for entity in entities:
        registry.add_entity(entity)

    return registry


if __name__ == "__main__":

    registry = build_islamic_registry()

    print("=" * 60)
    print("FaithAI — Islamic Entity Registry")
    print("=" * 60)

    stats = registry.statistics()

    print(
        f"Total Islamic entities: "
        f"{stats['total_entities']}"
    )

    print("\nEntities:")

    for entity in registry.entities.values():
        print(
            f"- {entity.name}"
            f" [{entity.entity_type}]"
            f" ({entity.entity_id})"
        )

    print("\nScriptures:")

    for entity in registry.list_by_type("scripture"):
        print(
            f"- {entity.name}"
        )

    print("\nDivine concepts:")

    for entity in registry.list_by_type(
        "divine_concept"
    ):
        print(
            f"- {entity.name}"
        )