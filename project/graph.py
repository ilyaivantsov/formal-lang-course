import cfpq_data
import networkx as nx
from collections import namedtuple
from typing import Set, Tuple, Dict, Any, Iterable
from scipy.sparse import dok_matrix

import numpy as np
from pyformlang.cfg.cfg import CFG, Variable

from project.cfg import cfg_to_whnf

GraphInfo = namedtuple("GraphInfo", ["nodes_count", "edges_count", "labels_set"])


def load_graph(name: str) -> nx.MultiDiGraph:
    """Loads graph by name."""
    return cfpq_data.graph_from_csv(cfpq_data.download(name))


def save_graph(graph: nx.MultiDiGraph, path: str):
    nx.drawing.nx_pydot.write_dot(graph, path)


def graph_info(graph: nx.MultiDiGraph) -> GraphInfo:
    """Returns summary about graph :class:`nx.MultiDiGraph`"""
    return GraphInfo(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        set([d["label"] for _, _, d in graph.edges(data=True)]),
    )


def create_two_cycles_graph(
        n: int, m: int, labels: tuple = ("a", "b")
) -> nx.MultiDiGraph:
    return cfpq_data.labeled_two_cycles_graph(n, m, labels=labels)


def create_and_save_two_cycles_graph(
        path: str, n: int, m: int, labels: tuple = ("a", "b")
):
    save_graph(graph=create_two_cycles_graph(n=n, m=m, labels=labels), path=path)


def get_graph_info_by_name(name: str) -> GraphInfo:
    return graph_info(load_graph(name=name))


def hellings_cfpq(cfg: CFG, graph: nx.MultiDiGraph) -> Set[Tuple]:
    """
    Hellings' algorithm
    """
    cfg = cfg_to_whnf(cfg)

    queue = []
    result = set()

    for prod in cfg.productions:
        if len(prod.body) == 0:
            for node in graph.nodes:
                t = (node, prod.head, node)
                result.add(t)
                queue.append(t)
        elif len(prod.body) == 1:
            for u, v, symb in graph.edges.data(data="label"):
                if Variable(symb) == prod.body[0]:
                    t = (u, prod.head, v)
                    result.add(t)
                    queue.append(t)

    while len(queue) != 0:
        u, var, v = queue.pop(0)
        diff = set()
        for uu, var1, vv in result:
            if vv == u:
                for prod in cfg.productions:
                    if prod.body == [var1, var]:
                        diff.add((uu, prod.head, v))
            if uu == v:
                for prod in cfg.productions:
                    if prod.body == [var, var1]:
                        diff.add((u, prod.head, vv))
        diff = diff.difference(result)
        queue.extend(diff)
        result = result.union(diff)
    return result


def query_cfg_graph(
        cfg: CFG, graph: nx.MultiDiGraph, S: Variable, starts: Iterable, finals: Iterable
) -> Dict[Any, Set]:
    """
    Query graph representing a finite automaton with a context-free grammar
    Parameters
    ----------
    """
    result = {u: set() for u in starts}
    tuples = hellings_cfpq(cfg, graph)
    for u, var1, v in tuples:
        if var1 == S and u in starts and v in finals:
            result[u].add(v)
    return result


def apply_matrix_alg(cfg: CFG, graph: nx.MultiDiGraph) -> Set[Tuple]:
    """
    Apply matrix algorithm to a graph
    """
    cfg = cfg_to_whnf(cfg)
    node_idx = {v: i for i, v in enumerate(graph.nodes)}
    n = len(node_idx)
    matrices = {var: dok_matrix((n, n), dtype=np.bool_) for var in cfg.variables}
    for prod in cfg.productions:
        if len(prod.body) == 0:
            for i in range(n):
                matrices[prod.head][i, i] = True
        elif len(prod.body) == 1:
            for u, v, symb in graph.edges.data(data="label"):
                if Variable(symb) == prod.body[0]:
                    i = node_idx[u]
                    j = node_idx[v]
                    matrices[prod.head][i, j] = True

    while True:
        matrices_changed = False

        # Matrix multiplication
        for prod in cfg.productions:
            if len(prod.body) != 2:
                continue
            for var_a in matrices:
                for var_b in matrices:
                    if [var_a, var_b] != prod.body:
                        continue

                    for i in range(n):
                        for j in range(n):
                            for k in range(n):
                                if matrices[var_a][i, j] and matrices[var_b][j, k] and not matrices[prod.head][i, k]:
                                    matrices[prod.head][i, k] = True
                                    matrices_changed = True

        if not matrices_changed:
            break

    result = set()
    nodes = list(graph.nodes)
    for var in cfg.variables:
        xs, ys = matrices[var].nonzero()
        for i in range(len(xs)):
            result.add((nodes[xs[i]], var, nodes[ys[i]]))
    return result
