"""Демонстрація варіанту 6 і ліміту рекурсії CPython."""

import copy
import sys

from nested import (
    Nested,
    flatten,
    freeze,
    make_deep,
    max_depth,
    nested_count,
    nested_stats,
    nested_stats_cached,
    nested_stats_iter,
    nested_sum,
    nested_sum_trampoline,
)

DATA: Nested = [3, [1.5, 2, (4, [])], [[[10]]], (), [7, [8, [9]]]]
SNAPSHOT = copy.deepcopy(DATA)


def main() -> None:
    print(f"Структура: {DATA}")
    print(f"nested_sum   = {nested_sum(DATA)}")
    print(f"nested_count = {nested_count(DATA)}")
    print(f"max_depth    = {max_depth(DATA)}")
    print(f"flatten      = {list(flatten(DATA))}")
    print(f"nested_stats (рекурсивно, 1 прохід) = {nested_stats(DATA)}")
    print(f"nested_stats_iter (власний стек)    = {nested_stats_iter(DATA)}")
    print(f"nested_sum_trampoline               = {nested_sum_trampoline(DATA)}")
    print(f"Вхідні дані не змінено: {DATA == SNAPSHOT}")

    print("\n=== lru_cache на повторюваних піддеревах ===")
    block = freeze([[1, 2, 3], [4, 5, [6, 7]]])
    shared = (block, block, (block, block), block)  # одне й те саме піддерево 5 разів
    nested_stats_cached.cache_clear()
    print(f"nested_stats_cached = {nested_stats_cached(shared)}")
    print(nested_stats_cached.cache_info())
    nested_stats_cached.cache_clear()
    print(f"після cache_clear(): {nested_stats_cached.cache_info()}")

    print("\n=== Ліміт рекурсії та відсутність TCO ===")
    print(f"sys.getrecursionlimit() = {sys.getrecursionlimit()}")
    for depth in (450, 600, 100_000):
        deep = make_deep(depth)
        try:
            rec = str(nested_sum(deep))
        except RecursionError:
            rec = "RecursionError"
        print(
            f"глибина {depth:>7}: рекурсивно -> {rec:<15} "
            f"ітеративно -> {nested_stats_iter(deep)}  "
            f"трамплін -> {nested_sum_trampoline(deep)}"
        )


if __name__ == "__main__":
    main()
