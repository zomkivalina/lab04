"""Порівняння часу: рекурсія vs ітерація, з кешем vs без кешу."""

import random
import timeit
from collections.abc import Callable
from functools import partial

from algorithms import fib, fib_iter, fib_naive, hybrid_quicksort, quicksort
from nested import (
    Frozen,
    Nested,
    freeze,
    nested_stats,
    nested_stats_cached,
    nested_stats_iter,
)


def tree(width: int, depth: int, leaf: Callable[[], int] = lambda: 1) -> Nested:
    """Збалансована вкладена структура: width^depth чисел."""
    if depth == 0:
        return leaf()
    return [tree(width, depth - 1, leaf) for _ in range(width)]


def ms(fn: Callable[[], object], number: int = 3) -> float:
    return min(timeit.repeat(fn, number=number, repeat=3)) / number * 1000


def row(name: str, value: float) -> None:
    print(f"{name:<44} {value:>10.3f} мс")


def main() -> None:
    for title, data in (
        ("однакові піддерева", tree(4, 8)),
        ("випадкові числа", tree(4, 8, lambda: random.randint(0, 9))),
    ):
        frozen = freeze(data)
        print(f"=== Варіант 6: 4^8 = 65 536 чисел, глибина 8, {title} ===")
        row("nested_stats (рекурсія)", ms(partial(nested_stats, data)))
        row("nested_stats_iter (власний стек)", ms(partial(nested_stats_iter, data)))

        def cached_cold(f: Frozen = frozen) -> object:
            nested_stats_cached.cache_clear()
            return nested_stats_cached(f)

        row("nested_stats_cached (порожній кеш)", ms(cached_cold))
        nested_stats_cached.cache_clear()
        nested_stats_cached(frozen)
        print(f"  {nested_stats_cached.cache_info()}")
        print()

    print("=== Фібоначчі ===")
    for n in (20, 25, 30):
        naive = ms(partial(fib_naive, n), number=1)

        def memo(n: int = n) -> int:
            fib.cache_clear()
            return fib(n)

        print(
            f"n={n}: naive {naive:>9.3f} мс | lru_cache {ms(memo, 100):.4f} мс | "
            f"iter {ms(partial(fib_iter, n), 100):.4f} мс"
        )

    print("\n=== Сортування 20 000 чисел з дублікатами ===")
    xs = [random.randint(0, 500) for _ in range(20_000)]
    row("quicksort (3-way, random pivot)", ms(lambda: quicksort(xs)))
    row("hybrid_quicksort (insertion < 32)", ms(lambda: hybrid_quicksort(xs)))
    row("sorted (Timsort, C)", ms(lambda: sorted(xs)))


if __name__ == "__main__":
    main()
