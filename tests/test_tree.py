from algorithms import (
    Node,
    bfs_level_order,
    dfs_preorder_iter,
    height,
    inorder,
    postorder,
    preorder,
)


def sample_tree() -> Node:
    #      4
    #    /   \
    #   2     6
    #  / \     \
    # 1   3     7
    return Node(4, Node(2, Node(1), Node(3)), Node(6, None, Node(7)))


def test_traversals() -> None:
    t = sample_tree()
    assert list(preorder(t)) == [4, 2, 1, 3, 6, 7]
    assert list(inorder(t)) == [1, 2, 3, 4, 6, 7]
    assert list(postorder(t)) == [1, 3, 2, 7, 6, 4]
    assert bfs_level_order(t) == [4, 2, 6, 1, 3, 7]
    assert dfs_preorder_iter(t) == list(preorder(t))


def test_empty_and_single() -> None:
    assert list(preorder(None)) == [] and bfs_level_order(None) == []
    assert dfs_preorder_iter(Node(1)) == [1]
    assert height(None) == 0 and height(sample_tree()) == 3
