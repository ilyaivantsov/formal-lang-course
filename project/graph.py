import cfpq_data
import networkx as nx
from collections import namedtuple
from typing import Set, Tuple, Dict, Any, Iterable
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