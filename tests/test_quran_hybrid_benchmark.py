
"""Compare existing lexical, direct lexical, and hybrid Qur'an retrieval."""

from statistics import mean
from time import perf_counter

from rag.retrieval.quran_lexical_retriever import QuranLexicalRetriever
from rag.retrieval.quran_hybrid_retriever import QuranHybridRetriever


BENCHMARKS = {
    "Patience": {
        "query": "الصبر",
        "targets": {
            "quran.2.153", "quran.2.155", "quran.2.156",
            "quran.2.157", "quran.3.200", "quran.16.127",
            "quran.12.18", "quran.12.83", "quran.42.43",
            "quran.46.35", "quran.103.3",
        },
    },
    "Hardship": {
        "query": "الشدّة",
        "targets": {
            "quran.2.155", "quran.2.156", "quran.2.214",
            "quran.3.186", "quran.4.28", "quran.94.5",
            "quran.94.6",
        },
    },
    "Forgiveness": {
        "query": "المغفرة",
        "targets": {
            "quran.2.199", "quran.3.133", "quran.3.134",
            "quran.4.110", "quran.7.199", "quran.24.22",
            "quran.39.53",
        },
    },
    "Prayer": {
        "query": "الصلاة",
        "targets": {
            "quran.2.43", "quran.2.110", "quran.2.238",
            "quran.4.103", "quran.11.114", "quran.17.78",
            "quran.29.45",
        },
    },
}


def passage_id(result):
    return result.passage.passage_id


def calculate_metrics(results, targets, k=5, recall_k=10):
    ranked_ids = [passage_id(item) for item in results]
    top_k = ranked_ids[:k]
    top_recall = ranked_ids[:recall_k]

    relevant_at_k = sum(pid in targets for pid in top_k)
    relevant_at_recall_k = sum(pid in targets for pid in top_recall)

    first_relevant_rank = next(
        (rank for rank, pid in enumerate(ranked_ids, 1)
         if pid in targets),
        None,
    )

    return {
        "precision5": relevant_at_k / k,
        "recall10": relevant_at_recall_k / len(targets),
        "mrr": 1 / first_relevant_rank if first_relevant_rank else 0.0,
    }


def main():
    print("Building lexical retriever...")
    lexical = QuranLexicalRetriever()

    print("Building hybrid retriever...")
    hybrid = QuranHybridRetriever(lexical_retriever=lexical)

    systems = {
        "Existing lexical": lambda query: lexical.retrieve(
            query, limit=10
        ),
        "Direct lexical": lambda query: lexical.retrieve(
            query, limit=10, include_expansions=False
        ),
        "Hybrid": lambda query: hybrid.retrieve(
            query, limit=10
        ),
    }

    aggregate = {name: [] for name in systems}

    for concept, benchmark in BENCHMARKS.items():
        print("\n" + "=" * 68)
        print(f"{concept}: {benchmark['query']}")
        print(f"Known target examples: {len(benchmark['targets'])}")

        for system_name, retrieve in systems.items():
            started = perf_counter()
            results = retrieve(benchmark["query"])
            latency_ms = (perf_counter() - started) * 1000

            metrics = calculate_metrics(
                results, benchmark["targets"]
            )
            aggregate[system_name].append(metrics)

            print(
                f"\n{system_name} | {latency_ms:.2f} ms\n"
                f"  P@5={metrics['precision5']:.3f}  "
                f"R@10={metrics['recall10']:.3f}  "
                f"MRR={metrics['mrr']:.3f}"
            )

            for rank, result in enumerate(results[:10], 1):
                pid = passage_id(result)
                marker = " [KNOWN TARGET]" if pid in benchmark["targets"] else ""
                print(f"  {rank:2}. {pid}{marker}")

    print("\n" + "=" * 68)
    print("AGGREGATE RESULTS")
    print("=" * 68)

    for system_name, rows in aggregate.items():
        print(
            f"{system_name:18} "
            f"P@5={mean(x['precision5'] for x in rows):.3f}  "
            f"R@10={mean(x['recall10'] for x in rows):.3f}  "
            f"MRR={mean(x['mrr'] for x in rows):.3f}"
        )

    print(
        "\nReminder: target lists are manually selected examples, "
        "not exhaustive relevance judgments."
    )


if __name__ == "__main__":
    main()
