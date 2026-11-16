from collections.abc import Callable

import pytest

from algorithms import fib, fib_iter, fib_naive


def test_fib_small() -> None:
    assert [fib(i) for i in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_versions_match() -> None:
    for n in range(25):
        assert fib(n) == fib_iter(n) == fib_naive(n)
    assert fib(90) == fib_iter(90) == 2880067194370816120


def test_cache_info_and_clear() -> None:
    fib.cache_clear()
    fib(30)
    assert fib.cache_info().misses == 31  # кожне n від 0 до 30 — рівно один раз
    fib.cache_clear()
    assert fib.cache_info().currsize == 0


@pytest.mark.parametrize("f", [fib, fib_iter, fib_naive])
def test_negative_rejected(f: Callable[[int], int]) -> None:
    with pytest.raises(ValueError):
        f(-1)
