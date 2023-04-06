import pytest

from project.dfa_utils import query_bfs
from project.graph import create_two_cycles_graph


def test_1():
    regex = r"a (a a | b b b)*"
    graph = create_two_cycles_graph(1, 2)

    got = query_bfs(regex, graph, [0, 1], [0, 1], type=True)
    assert {0, 1} == got


def test_2():
    regex = r"a (a a | b b b)*"
    graph = create_two_cycles_graph(1, 2)

    got = query_bfs(regex, graph, [0, 1], [0, 1], type=False)
    assert {0: {1}, 1: {0}} == got
