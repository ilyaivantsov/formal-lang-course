import networkx as nx
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton


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
