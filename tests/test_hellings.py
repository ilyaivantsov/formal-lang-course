from pyformlang.cfg import CFG, Variable
from project.graph import create_two_cycles_graph, query_cfg_graph


def test_query_cfg_sf():
    cfg = CFG.from_text(
        """
        S -> A B
        S -> A S1
        S1 -> S B
        A -> a
        B -> b
        """
    )
    g = create_two_cycles_graph(2, 1)
    result = query_cfg_graph(cfg, g, Variable("S"), [0, 1, 2, 3], [0, 1, 2, 3])
    assert result == {
        0: {0, 3},
        1: {0, 3},
        2: {0, 3},
        3: set(),
    }
