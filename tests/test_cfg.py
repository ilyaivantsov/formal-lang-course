import os
import tempfile

from pyformlang.cfg import Variable, Terminal

import project.cfg as CFD


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
