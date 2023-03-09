from typing import Tuple, Dict, Iterable
from pyformlang.finite_automaton import State
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import EpsilonNFA
import networkx as nx
from scipy.sparse import dok_matrix, kron
import numpy as np


def regex2dfa(expr: str) -> DeterministicFiniteAutomaton:
    dfa = Regex(expr).to_epsilon_nfa()
    return dfa.minimize()


def graph2nfa(
    graph: nx.MultiDiGraph, starts, finals
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transitions([(v, d["label"], u) for v, u, d in graph.edges(data=True)])

    for node in starts:
        nfa.add_start_state(node)
    for node in finals:
        nfa.add_final_state(node)
    return nfa


def nfa_to_bool_matrices(
    nfa: EpsilonNFA,
) -> Tuple[Dict[State, int], Dict[any, dok_matrix], Iterable[str], Iterable[str]]:
    state_to_inx = {k: i for i, k in enumerate(nfa.states)}
    n_states = len(nfa.states)
    result = dict()
    for v, s, u in nfa:
        result.setdefault(s, dok_matrix((n_states, n_states), dtype=np.bool_))[
            state_to_inx[v], state_to_inx[u]
        ] = 1
    return state_to_inx, result, nfa.start_states, nfa.final_states


def nfa_to_intersect_matrices(
    nfa1: EpsilonNFA, nfa2: EpsilonNFA
) -> Tuple[Dict[State, int], Dict[any, dok_matrix], Iterable[str], Iterable[str]]:
    nfa1_state_to_inx, nfa1_matrices, ss1, fs1 = nfa_to_bool_matrices(nfa1)
    nfa2_state_to_inx, nfa2_matrices, ss2, fs2 = nfa_to_bool_matrices(nfa2)
    result_state_to_inx = dict(nfa1_state_to_inx.items() & nfa2_state_to_inx.items())
    symbols = set(nfa1_matrices.keys()).intersection(nfa2_matrices.keys())
    result_state_matrices = {
        s: kron(nfa1_matrices[s], nfa1_matrices[s]) for s in symbols
    }
    return (
        result_state_to_inx,
        result_state_matrices,
        set(ss1) & set(ss2),
        set(fs1) & set(fs2),
    )


def from_matrices_to_nfa(matrices: Dict[any, dok_matrix]) -> EpsilonNFA:
    nfa = EpsilonNFA()

    for symbol, matrix in matrices.items():
        for v, _, u in zip(matrix.row, matrix.col, matrix.data):
            if u:
                nfa.add_transition(v, symbol, u)

    return nfa
