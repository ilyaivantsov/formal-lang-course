from typing import Tuple, Dict, Iterable, Any, Set
from pyformlang.finite_automaton import State
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import EpsilonNFA
import networkx as nx
from scipy.sparse import dok_matrix, kron, eye, block_diag
import numpy as np


def regex2dfa(expr: str) -> DeterministicFiniteAutomaton:
    """Return minimized DFA from regular expression string

    Keyword arguments:
    expr -- academic regular expression string;
    """
    dfa = Regex(expr).to_epsilon_nfa()
    return dfa.minimize()


def graph2nfa(
    graph: nx.MultiDiGraph,
    starts: Iterable[Any] = None,
    finals: Iterable[Any] = None,
) -> NondeterministicFiniteAutomaton:
    """Return nondeterministic finite automaton from :class:`nx.MultiDiGraph` graph

    Keyword arguments:
    graph -- source graph;
    starts -- `graph's` nodes marked as starts;
    finals -- `graph's` nodes marked as finals;
    """
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transitions([(v, d["label"], u) for v, u, d in graph.edges(data=True)])

    if starts is not None:
        for node in starts:
            nfa.add_start_state(node)
    if finals is not None:
        for node in finals:
            nfa.add_final_state(node)
    return nfa


def nfa_to_bool_matrices(
    nfa: EpsilonNFA,
) -> Tuple[Dict[State, int], Dict[Any, dok_matrix], Iterable[Any], Iterable[Any]]:
    """Convert finite automaton :class:`EpsilonNFA` to the transition matrix dictionary

    Keyword arguments:
    nfa -- source graph;
    """
    state_to_inx = {k: i for i, k in enumerate(nfa.states)}
    n_states = len(nfa.states)
    result = dict()
    for v, s, u in nfa:
        result.setdefault(s, dok_matrix((n_states, n_states), dtype=np.bool_))[
            state_to_inx[v], state_to_inx[u]
        ] = 1
    return state_to_inx, result, nfa.start_states, nfa.final_states


def nfa_intersect(nfa1: EpsilonNFA, nfa2: EpsilonNFA) -> EpsilonNFA:
    """Intersection of two finite automatons"""
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
) -> Set[Tuple[State, State]]:
    """Finds all pairs of start and end states such that the end state is reachable from the start state
    with the restrictions specified in the regular expression."""
    g1 = regex2dfa(regex)
    g2 = graph2nfa(graph, start_states, final_states)
    result_i = nfa_intersect(g1, g2)

    state_to_inx, matrices, start_states_r, final_states_r = nfa_to_bool_matrices(
        result_i
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


def BFSBasedRPQ_util(
    regex_dfa: DeterministicFiniteAutomaton,
    regex_idx: Dict[Any, int],
    n_graph: int,
    node_names: Dict[int, Any],
    transitions: Dict,
    starts: Iterable[int],
) -> Set:
    """
    Find nodes in graph, accessible from at least one of the selected starting nodes.
    """
    n_regex = len(regex_dfa.states)
    m_graph = n_regex + n_graph

    M = eye(n_regex, m_graph, dtype=np.bool_, format="dok")

    for rs in regex_dfa.start_states:
        i = regex_idx[rs]
        for s in starts:
            M[i, n_regex + s] = True

    prev = 0
    front = M
    while M.count_nonzero() != prev:
        prev = M.count_nonzero()
        new_front = eye(n_regex, m_graph, dtype=np.bool_, format="dok")
        for matrix in transitions.values():
            next = front @ matrix
            for i in range(n_regex):
                for j in range(n_regex):
                    if next[i, j]:
                        new_front[j, n_regex:] += next[i, n_regex:]
        M += new_front
        front = new_front

    result = set()
    for fs in regex_dfa.final_states:
        fs_id = regex_idx[fs]
        for i in range(n_graph):
            if M[fs_id, n_regex + i]:
                result.add(node_names[i])
    return result


def BFSBasedRPQ_type(
    regex: str, graph: nx.MultiDiGraph, starts: Iterable, type=True
) -> Set | Dict:
    """
    Find nodes in graph, accessible from nodes depending on the type.
    Returns
    -------
    Set or Dict of accessible nodes
    """
    regex_dfa = regex2dfa(regex)
    regex_idx, regex_mat, _, _ = nfa_to_bool_matrices(regex_dfa)
    graph_idx, graph_mat, _, _ = nfa_to_bool_matrices(graph2nfa(graph, starts, starts))

    common_symbols = set(regex_mat.keys()).intersection(graph_mat.keys())
    transitions = {
        s: block_diag((regex_mat[s], graph_mat[s]), format="dok")
        for s in common_symbols
    }
    graph_names = {v: k for k, v in graph_idx.items()}

    if type:
        start_idx = [graph_idx[s] for s in starts]
        return BFSBasedRPQ_util(
            regex_dfa, regex_idx, len(graph_idx), graph_names, transitions, start_idx
        )
    else:
        result = dict()
        for s in starts:
            result[s] = BFSBasedRPQ_util(
                regex_dfa,
                regex_idx,
                len(graph_idx),
                graph_names,
                transitions,
                [graph_idx[s]],
            )
        return result


def query_bfs(
    regex: str, graph: nx.MultiDiGraph, starts: Iterable, finals: Iterable, type=True
) -> Set | Dict:
    if type:
        return BFSBasedRPQ_type(regex, graph, starts, type).intersection(set(finals))
    else:
        return {
            k: v.intersection(set(finals))
            for k, v in BFSBasedRPQ_type(regex, graph, starts, type).items()
        }
