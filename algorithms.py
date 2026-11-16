"""Базова частина: quicksort, обходи дерева, Фібоначчі з мемоізацією."""

from __future__ import annotations

import random
from collections import deque
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache

# ---------- Quicksort ----------


def quicksort(xs: Sequence[int], rng: random.Random | None = None) -> list[int]:
    """Рекурсивний 3-шляховий quicksort з випадковим pivot. Вхід не змінюється."""
    if len(xs) <= 1:  # база: 0 або 1 елемент уже відсортовано
        return list(xs)
    pick = rng.choice if rng else random.choice
    p = pick(xs)
    left = [x for x in xs if x < p]
    mid = [x for x in xs if x == p]  # усі дублікати pivot — одразу на місці
    right = [x for x in xs if x > p]
    return quicksort(left, rng) + mid + quicksort(right, rng)


def insertion_sort(xs: Sequence[int]) -> list[int]:
    out: list[int] = []
    for x in xs:
        i = len(out)
        while i > 0 and out[i - 1] > x:
            i -= 1
        out.insert(i, x)
    return out


def hybrid_quicksort(xs: Sequence[int], threshold: int = 32) -> list[int]:
    """Підмасиви, коротші за threshold, сортуються вставками (менше викликів)."""
    if len(xs) < threshold:
        return insertion_sort(xs)
    p = random.choice(xs)
    return (
        hybrid_quicksort([x for x in xs if x < p], threshold)
        + [x for x in xs if x == p]
        + hybrid_quicksort([x for x in xs if x > p], threshold)
    )


# ---------- Дерево та обходи ----------


@dataclass(frozen=True, slots=True)
class Node:
    key: int
    left: Node | None = None
    right: Node | None = None


def preorder(t: Node | None) -> Iterator[int]:
    if t is None:
        return
    yield t.key
    yield from preorder(t.left)
    yield from preorder(t.right)


def inorder(t: Node | None) -> Iterator[int]:
    if t is None:
        return
    yield from inorder(t.left)
    yield t.key
    yield from inorder(t.right)


def postorder(t: Node | None) -> Iterator[int]:
    if t is None:
        return
    yield from postorder(t.left)
    yield from postorder(t.right)
    yield t.key


def bfs_level_order(t: Node | None) -> list[int]:
    out: list[int] = []
    queue = deque([t] if t else [])
    while queue:
        n = queue.popleft()
        out.append(n.key)
        queue.extend(c for c in (n.left, n.right) if c)
    return out


def dfs_preorder_iter(t: Node | None) -> list[int]:
    out: list[int] = []
    stack = [t] if t else []
    while stack:
        n = stack.pop()
        out.append(n.key)
        stack.extend(c for c in (n.right, n.left) if c)  # правий першим у стек
    return out


def height(t: Node | None) -> int:
    if t is None:
        return 0
    return 1 + max(height(t.left), height(t.right))


# ---------- Фібоначчі ----------


def fib_naive(n: int) -> int:
    """Без кешу: O(φ^n) — ті самі підзадачі рахуються знову і знову."""
    if n < 0:
        raise ValueError("n має бути >= 0")
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


@lru_cache(maxsize=None)
def fib(n: int) -> int:
    """З мемоізацією: O(n) за часом, але глибина стеку теж O(n)."""
    if n < 0:
        raise ValueError("n має бути >= 0")
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def fib_iter(n: int) -> int:
    if n < 0:
        raise ValueError("n має бути >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
