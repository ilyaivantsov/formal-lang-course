import pytest
from typing import Dict
from project.ecfg import ECFG
from pyformlang.cfg import CFG, Variable
from pyformlang.regular_expression import Regex


@pytest.mark.parametrize(
    "text, expected",
    [
        ("S -> epsilon", {Variable("S"): Regex("$")}),
        ("S -> epsilon | a S b S", {Variable("S"): Regex("$ | a S b S")}),
    ],
)
def test_1(text: str, expected: Dict[Variable, Regex]):
    ecfg = ECFG.from_cfg(CFG.from_text(text))
    assert ecfg.productions.keys() == expected.keys()
    for key in expected:
        nfa1 = ecfg.productions[key].to_epsilon_nfa()
        nfa2 = expected[key].to_epsilon_nfa()
        assert nfa1.is_equivalent_to(nfa2)
