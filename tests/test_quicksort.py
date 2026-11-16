import random
from collections.abc import Callable, Sequence

import pytest

from algorithms import hybrid_quicksort, insertion_sort, quicksort

Sort = Callable[[Sequence[int]], list[int]]


@pytest.mark.parametrize("sort", [quicksort, hybrid_quicksort, insertion_sort])
def test_basic(sort: Sort) -> None:
    assert sort([]) == []
    assert sort([1]) == [1]
    assert sort([3, 2, 1]) == [1, 2, 3]
    assert sort([2, 2, 1, 3, 2]) == [1, 2, 2, 2, 3]


@pytest.mark.parametrize("sort", [quicksort, hybrid_quicksort])
def test_random_against_sorted(sort: Sort) -> None:
    xs = [random.randint(-1000, 1000) for _ in range(2000)]
    assert sort(xs) == sorted(xs)


def test_many_duplicates_and_sorted_input() -> None:
    dup = [5] * 5000 + [1] * 5000  # 3-way partition: без глибокої рекурсії
    assert quicksort(dup) == sorted(dup)
    already = list(range(3000))
    assert quicksort(already) == already


def test_does_not_mutate_and_accepts_tuple() -> None:
    xs = [3, 1, 2]
    assert quicksort(tuple(xs)) == [1, 2, 3]
    quicksort(xs)
    assert xs == [3, 1, 2]


def test_reproducible_with_seeded_rng() -> None:
    xs = [random.randint(0, 99) for _ in range(500)]
    assert quicksort(xs, random.Random(1)) == quicksort(xs, random.Random(2))
