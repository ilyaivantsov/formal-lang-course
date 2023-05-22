import tempfile

from pyformlang.cfg import Variable, Terminal
from pyformlang.cfg.cfg import CFG
import project.cfg as CFD
from project.graph import create_two_cycles_graph, apply_matrix_alg


def test_read_cfg_from_file():
    with tempfile.NamedTemporaryFile(mode="tw+", delete=False) as file:
        file.write("\n".join(["S->A|B|C", "A->a", "B->b", "C->C"]))
        name = file.name
    cfg = CFD.cfg_from_file(name)
    assert cfg.contains("a")
    assert cfg.contains("b")
    assert not cfg.contains("c")


def test_wnf():
    with tempfile.NamedTemporaryFile(mode="tw+", delete=False) as file:
        file.write("\n".join(["S->A B|B S|C", "A->a", "B->b b b", "C->C c"]))
        name = file.name
    cfg = CFD.cfg_from_file(name)
    cfg = CFD.cfg_to_whnf(cfg)

    assert Variable("A") in cfg.variables
    assert Variable("B") in cfg.variables
    assert Variable("S") in cfg.variables
    assert Variable("C") not in cfg.variables

    assert Terminal("a") in cfg.terminals
    assert Terminal("b") in cfg.terminals
    assert Terminal("c") not in cfg.terminals


def test_matrices():
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
    result = apply_matrix_alg(cfg, g)

    assert result == {
        (1, Variable("A"), 2),
        (2, Variable("A"), 0),
        (0, Variable("A"), 1),
        (3, Variable("B"), 0),
        (0, Variable("B"), 3),
        (0, Variable("S1"), 3),
        (2, Variable("S"), 3),
        (2, Variable("S1"), 0),
        (1, Variable("S"), 0),
        (1, Variable("S1"), 3),
        (0, Variable("S"), 3),
        (0, Variable("S1"), 0),
        (2, Variable("S"), 0),
        (2, Variable("S1"), 3),
        (1, Variable("S"), 3),
        (1, Variable("S1"), 0),
        (0, Variable("S"), 0),
    }
