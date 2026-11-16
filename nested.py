"""Варіант 6: сума, кількість елементів і глибина вкладених list/tuple чисел.

Вкладена структура визначається рекурсивно:
    Nested = int | float | list[Nested] | tuple[Nested, ...]

База рекурсії:  число            -> сума = саме число, кількість = 1, глибина = 0
                порожній список  -> сума = 0, кількість = 0, глибина = 1
Крок рекурсії:  контейнер        -> результат для кожного елемента + об'єднання.
"""

from collections.abc import Callable, Iterator
from functools import lru_cache

type Number = int | float
type Nested = Number | list[Nested] | tuple[Nested, ...]
type Frozen = Number | tuple[Frozen, ...]  # хешований варіант для lru_cache
type Stats = tuple[Number, int, int]  # (сума, кількість, глибина)


def _check_leaf(x: object) -> Number:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise TypeError(
            f"очікувалось число, list або tuple, отримано {type(x).__name__}"
        )
    return x


# ---------- Рекурсивні версії ----------


def nested_sum(data: Nested) -> Number:
    if isinstance(data, (list, tuple)):
        return sum((nested_sum(x) for x in data), 0)  # крок рекурсії
    return _check_leaf(data)  # база


def nested_count(data: Nested) -> int:
    if isinstance(data, (list, tuple)):
        return sum(nested_count(x) for x in data)
    _check_leaf(data)
    return 1


def max_depth(data: Nested) -> int:
    """Глибина вкладеності: число — 0, [1, 2] — 1, [1, [2]] — 2, [] — 1."""
    if isinstance(data, (list, tuple)):
        return 1 + max((max_depth(x) for x in data), default=0)
    _check_leaf(data)
    return 0


def nested_stats(data: Nested) -> Stats:
    """Сума, кількість і глибина за ОДИН рекурсивний прохід."""
    if not isinstance(data, (list, tuple)):
        return _check_leaf(data), 1, 0
    parts = [nested_stats(x) for x in data]
    return (
        sum((p[0] for p in parts), 0),
        sum(p[1] for p in parts),
        1 + max((p[2] for p in parts), default=0),
    )


def flatten(data: Nested) -> Iterator[Number]:
    """Рекурсивний генератор: усі числа зліва направо."""
    if isinstance(data, (list, tuple)):
        for x in data:
            yield from flatten(x)
    else:
        yield _check_leaf(data)


# ---------- Мемоізація: повторювані незмінні підструктури ----------


@lru_cache(maxsize=None, typed=True)  # typed: 1 і 1.0 — різні ключі
def nested_stats_cached(data: Frozen) -> Stats:
    """Те саме, що nested_stats, але з кешем. Працює лише для tuple:
    tuple хешується, тож однакові піддерева рахуються один раз."""
    if not isinstance(data, tuple):
        return _check_leaf(data), 1, 0
    parts = [nested_stats_cached(x) for x in data]
    return (
        sum((p[0] for p in parts), 0),
        sum(p[1] for p in parts),
        1 + max((p[2] for p in parts), default=0),
    )


def freeze(data: Nested) -> Frozen:
    """list -> tuple рекурсивно, щоб структуру можна було передати в lru_cache."""
    if isinstance(data, (list, tuple)):
        return tuple(freeze(x) for x in data)
    return data


# ---------- Ітеративна версія з власним стеком ----------


def nested_stats_iter(data: Nested) -> Stats:
    """Без рекурсії: стек пар (елемент, глибина). Не обмежена лімітом CPython."""
    total: Number = 0
    count = 0
    deepest = 0
    stack: list[tuple[Nested, int]] = [(data, 0)]
    while stack:
        item, depth = stack.pop()
        if isinstance(item, (list, tuple)):
            deepest = max(deepest, depth + 1)
            stack.extend((x, depth + 1) for x in item)
        else:
            total += _check_leaf(item)
            count += 1
    return total, count, deepest


# ---------- Трамплін (моделювання TCO) ----------

type Thunk = Callable[[], Bounce]
type Bounce = Number | Thunk


def trampoline(step: Bounce) -> Number:
    """Викликає «наступний крок», доки не отримає готове число."""
    while callable(step):
        step = step()
    return step


def _sum_tr(todo: tuple[Nested, ...], acc: Number) -> Bounce:
    """Хвостова рекурсія: замість виклику повертаємо лямбду з наступним кроком."""
    if not todo:
        return acc
    head, rest = todo[0], todo[1:]
    if isinstance(head, (list, tuple)):
        return lambda: _sum_tr(tuple(head) + rest, acc)
    return lambda: _sum_tr(rest, acc + _check_leaf(head))


def nested_sum_trampoline(data: Nested) -> Number:
    return trampoline(lambda: _sum_tr((data,), 0))


def make_deep(depth: int, leaf: Number = 1) -> Nested:
    """[[[...[1]...]]] заданої глибини — збудовано циклом, без рекурсії."""
    result: Nested = leaf
    for _ in range(depth):
        result = [result]
    return result
