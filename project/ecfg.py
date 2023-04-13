from typing import AbstractSet, Dict

from dataclasses import dataclass
from scipy.sparse import dok_matrix

from pyformlang.cfg import CFG, Variable, Terminal
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex

import numpy as np


@dataclass
class RFA:
    """
    Recursive finite automaton
    """

    start_symbol: Variable
    dfas: Dict[Variable, DeterministicFiniteAutomaton]

    def to_matrices(self):
        all_states = set()
        for var, dfa in self.dfas.items():
            for x in dfa.states:
                all_states.add((var, x))
        state_idx = {k: i for i, k in enumerate(all_states)}
        n_states = len(state_idx)
        result = dict()
        for var, dfa in self.dfas.items():
            for fro, symb, to in dfa:
                mat = result.setdefault(
                    symb, dok_matrix((n_states, n_states), dtype=np.bool_)
                )
                mat[state_idx[(var, fro)], state_idx[(var, to)]] = True
        return result, state_idx


class ECFG:
    """
    Extended context-free grammar
    """

    def __init__(
        self,
        variables: AbstractSet[Variable] = None,
        terminals: AbstractSet[Terminal] = None,
        start_symbol: Variable = None,
        productions: Dict[Variable, Regex] = None,
    ):
        self.variables = variables or set()
        self.terminals = terminals or set()
        self.start_symbol = start_symbol
        self.productions = productions or dict()

    def __repr__(self):
        return "\n".join(f"{head} -> {body}" for head, body in self.productions.items())

    @staticmethod
    def from_text(text: str, start_symbol=Variable("S")):
        variables = set()
        terminals = set()
        productions = dict()
        for line1 in text.splitlines():
            line = line1.strip()
            if not line:
                continue

            production_objects = line.split("->")
            head_text, body_text = production_objects

            head = Variable(head_text.strip())

            variables.add(head)
            body = Regex(body_text)
            productions[head] = body

        return ECFG(variables, terminals, start_symbol, productions)

    @staticmethod
    def from_cfg(cfg: CFG):
        productions_lst: Dict[Variable, str] = dict()
        for prod in cfg.productions:
            lst = productions_lst.setdefault(prod.head.value, [])
            if prod.body:
                lst.append(".".join(str(e.value) for e in prod.body))
            else:
                lst.append("$")
        productions = {
            head: Regex(" | ".join(f"({elem})" for elem in body))
            for head, body in productions_lst.items()
        }

        return ECFG(
            cfg.variables,
            cfg.terminals,
            cfg.start_symbol,
            productions,
        )

    def to_rfa(self) -> RFA:
        return RFA(
            start_symbol=self.start_symbol,
            dfas={
                head: body.to_epsilon_nfa().minimize()
                for head, body in self.productions.items()
            },
        )
