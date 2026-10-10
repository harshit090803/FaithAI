
from rag.retrieval.quran_lexical_retriever import QuranLexicalRetriever
from rag.retrieval.quran_hybrid_retriever import QuranHybridRetriever


TARGETS = {
    "quran.2.199",
    "quran.3.133",
    "quran.3.134",
    "quran.4.110",
    "quran.7.199",
    "quran.24.22",
    "quran.39.53",
}


def passage_id(result):
    passage = result.passage

    if isinstance(passage, dict):
        return passage.get("id") or passage.get("passage_id")

    return (
        getattr(passage, "passage_id", None)
        or getattr(passage, "id", None)
    )


def rank_map(results):
    return {
        passage_id(result): rank
        for rank, result in enumerate(results, start=1)
    }


def inspect_targets(label, results):
    ranks = rank_map(results)

    print(f"\n{label}")
    print("-" * 72)

    for target in sorted(TARGETS):
        rank = ranks.get(target)
        print(f"{target}: rank {rank}" if rank else f"{target}: NOT FOUND")


def main():
    print("Building lexical retriever...")
    lexical = QuranLexicalRetriever()

    print("Building hybrid retriever...")
    hybrid = QuranHybridRetriever(lexical_retriever=lexical)

    query = "المغفرة"
    candidate_limit = 100

    terms = hybrid._concept_terms(query)

    print("\nConcept terms:")
    for term, weight in terms.items():
        print(f"  {term}: {weight}")

    direct = lexical.retrieve(
        query, limit=candidate_limit, include_expansions=False
    )
    expanded = lexical.retrieve(
        query, limit=candidate_limit, include_expansions=True
    )

    inspect_targets("DIRECT LEXICAL", direct)
    inspect_targets("EXPANDED LEXICAL", expanded)

    concept_rank_maps = {}

    for term in terms:
        results = lexical.retrieve(
            term, limit=candidate_limit, include_expansions=False
        )
        concept_rank_maps[term] = rank_map(results)
        inspect_targets(f"CONCEPT: {term}", results)

    hybrid_results = hybrid.retrieve(
        query, limit=candidate_limit, candidate_limit=candidate_limit
    )

    inspect_targets("HYBRID FINAL RANKING", hybrid_results)

    hybrid_by_id = {
        passage_id(result): result for result in hybrid_results
    }

    direct_ranks = rank_map(direct)
    expanded_ranks = rank_map(expanded)

    print("\nTARGET CHANNEL DIAGNOSTICS")
    print("=" * 90)

    for target in sorted(TARGETS):
        result = hybrid_by_id.get(target)

        print(f"\n{target}")
        print(f"  Direct rank:   {direct_ranks.get(target)}")
        print(f"  Expanded rank: {expanded_ranks.get(target)}")

        for term, ranks in concept_rank_maps.items():
            rank = ranks.get(target)
            if rank is not None:
                print(f"  Concept {term}: rank {rank}")

        if result is None:
            print("  Hybrid: NOT IN RETURNED CANDIDATES")
        else:
            print(f"  Hybrid rank:   {hybrid_results.index(result) + 1}")
            print(f"  Fusion score:  {result.fusion_score:.6f}")
            print(f"  Lexical rank:  {result.lexical_rank}")
            print(f"  Concept rank:  {result.concept_rank}")


if __name__ == "__main__":
    main()
