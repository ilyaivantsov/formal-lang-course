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
    graph: nx.MultiDiGraph,
    starts: Iterable[any] = None,
    finals: Iterable[any] = None,
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
) -> Tuple[Dict[State, int], Dict[any, dok_matrix], Iterable[any], Iterable[any]]:
    state_to_inx = {k: i for i, k in enumerate(nfa.states)}
    n_states = len(nfa.states)
    result = dict()
    for v, s, u in nfa:
        result.setdefault(s, dok_matrix((n_states, n_states), dtype=np.bool_))[
            state_to_inx[v], state_to_inx[u]
        ] = 1
    return state_to_inx, result, nfa.start_states, nfa.final_states


def nfa_intersect(nfa1: EpsilonNFA, nfa2: EpsilonNFA) -> EpsilonNFA:
    nfa1_state_to_inx, nfa1_matrices, ss1, fs1 = nfa_to_bool_matrices(nfa1)
    nfa2_state_to_inx, nfa2_matrices, ss2, fs2 = nfa_to_bool_matrices(nfa2)

    result = EpsilonNFA()
    symbols = set.intersection(set(nfa1_matrices.keys()), set(nfa2_matrices.keys()))
    result_matrices = {s: kron(nfa1_matrices[s], nfa1_matrices[s]) for s in symbols}

    for s, matrix in result_matrices.items():
        from_idx, to_idx = matrix.nonzero()
        for v, u in zip(from_idx, to_idx):
            result.add_transition(v, s, u)

    for s1 in ss1:
        for s2 in ss2:
            state = State(
                nfa1_state_to_inx[s1] * len(nfa2_state_to_inx) + nfa2_state_to_inx[s2]
            )
            result.add_start_state(state)

    for f1 in fs1:
        for f2 in fs2:
            state = State(
                nfa1_state_to_inx[f1] * len(nfa2_state_to_inx) + nfa2_state_to_inx[f2]
            )
            result.add_final_state(state)

    return result


def query(
    regex: str,
    graph: nx.MultiDiGraph,
    start_states,
    final_states,
) -> set[tuple[any, any]]:
    g1 = regex2dfa(regex)
    g2 = graph2nfa(graph, start_states, final_states)
    result = nfa_intersect(g1, g2)

    state_to_inx, matrices, start_states_r, final_states_r = nfa_to_bool_matrices(
        result
    )

    c_matrix = dok_matrix((len(state_to_inx), len(state_to_inx)), dtype=np.bool_)
    for matrix in matrices.values():
        c_matrix |= matrix

    flag = False
    while not flag:
        p1 = c_matrix.count_nonzero()
        c_matrix += c_matrix @ c_matrix
        flag = p1 == c_matrix.count_nonzero()

    result = set()
    mapping = {i: k for k, i in state_to_inx.items()}
    states_list = list(g2.states)
    n_states = len(g2.states)

    from_idx, to_idx = c_matrix.nonzero()
    for fro, to in zip(from_idx, to_idx):
        fro_id, to_id = mapping[fro], mapping[to]
        if fro_id in start_states_r and to_id in final_states_r:
            result.add(
                (
                    states_list[fro_id.value % n_states],
                    states_list[to_id.value % n_states],
                )
            )

    return result
