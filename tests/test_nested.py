import copy
import random

import pytest

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

SAMPLE: Nested = [1, [2, 3, (4.5, [])], [[[6]]], ()]


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (5, (5, 1, 0)),  # база: одне число
        ([], (0, 0, 1)),  # база: порожній список
        ((), (0, 0, 1)),
        ([[], [[]]], (0, 0, 3)),  # лише порожні контейнери
        ([1, 2, 3], (6, 3, 1)),
        ([-1, [1]], (0, 2, 2)),
        (SAMPLE, (16.5, 5, 4)),
    ],
)
def test_stats_edge_cases(data: Nested, expected: tuple[float, int, int]) -> None:
    assert nested_stats(data) == expected
    assert (nested_sum(data), nested_count(data), max_depth(data)) == expected


def test_all_versions_agree_on_random_structures() -> None:
    rng = random.Random(42)

    def gen(depth: int) -> Nested:
        if depth == 0 or rng.random() < 0.3:
            return rng.randint(-50, 50)
        kind = list if rng.random() < 0.5 else tuple
        return kind(gen(depth - 1) for _ in range(rng.randint(0, 4)))

    for _ in range(200):
        data = gen(6)
        expected = nested_stats(data)
        assert nested_stats_iter(data) == expected
        assert nested_stats_cached(freeze(data)) == expected
        assert nested_sum_trampoline(data) == expected[0]
        assert sum(flatten(data)) == expected[0]


def test_input_is_not_mutated() -> None:
    data: Nested = [1, [2, [3]], (4, [5])]
    snapshot = copy.deepcopy(data)
    nested_stats(data)
    nested_stats_iter(data)
    nested_sum_trampoline(data)
    list(flatten(data))
    assert data == snapshot


def test_flatten_order() -> None:
    assert list(flatten(SAMPLE)) == [1, 2, 3, 4.5, 6]


@pytest.mark.parametrize("bad", [[1, "2"], [None], [True], {"a": 1}])
def test_rejects_non_numbers(bad: object) -> None:
    with pytest.raises(TypeError):
        nested_sum(bad)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        nested_stats_iter(bad)  # type: ignore[arg-type]


def test_deep_structure_recursion_vs_iteration() -> None:
    deep = make_deep(10_000, leaf=7)
    with pytest.raises(RecursionError):
        nested_sum(deep)  # немає TCO — стек переповнюється
    assert nested_stats_iter(deep) == (7, 1, 10_000)
    assert nested_sum_trampoline(deep) == 7


def test_cache_info_and_clear() -> None:
    block = freeze([1, [2, 3]])
    shared = (block, block, block)
    nested_stats_cached.cache_clear()
    assert nested_stats_cached(shared) == (18, 9, 3)
    info = nested_stats_cached.cache_info()
    assert info.hits == 2  # block порахований один раз, двічі взятий з кешу
    nested_stats_cached.cache_clear()
    assert nested_stats_cached.cache_info().currsize == 0


def test_cache_requires_hashable_input() -> None:
    with pytest.raises(TypeError):
        nested_stats_cached([1, 2])  # type: ignore[arg-type]
