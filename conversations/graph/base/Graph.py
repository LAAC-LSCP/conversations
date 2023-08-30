#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: Graph.py (as part of project conversations)
#   Created: 06/07/2022 12:05
#   Last Modified: 06/07/2022 12:05
# -----------------------------------------------------------------------------
#   Author: William N. Havard
#           Postdoctoral Researcher
#
#   Mail  : william.havard@ens.fr / william.havard@gmail.com
#  
#   Institution: ENS / Laboratoire de Sciences Cognitives et Psycholinguistique
#
# ------------------------------------------------------------------------------
#   Description: 
#       • 
# -----------------------------------------------------------------------------

import abc
from typing import List, Set, Tuple

from conversations.graph.base.Node import Node


class Graph(abc.ABC):
    """
    Abstract class for a graph
    """

    def __init__(self):
        # Stores nodes and edges
        self.adjacency = dict()

    @classmethod
    def from_tuple_list(cls, tuple_list: List[Tuple[Node, Node]]):
        """
        Create a graph from a list of edges between nodes given as 2-uple (start_node, end_node)
        :param tuple_list: list of tuples
        :type tuple_list: List[Tuple[Node, Node]]
        :return: a graph
        :rtype: DirectedGraph
        """
        graph = cls()
        for node_tuple in tuple_list:
            graph.add_edge(*node_tuple)
        return graph

    @abc.abstractmethod
    def add_edge(self, node1: Node, node2: Node) -> None:
        pass

    @property
    def num_edges(self) -> int:
        """
        Returns the number of edges in the graph
        :return: number of edges in the graph
        :rtype: int
        """
        return len(list(self))

    @property
    def num_nodes(self) -> int:
        """
        Returns the number of nodes in the graph
        :return: number of nodes in the graph
        :rtype: int
        """
        return len(self.adjacency.keys())

    @property
    def start_nodes(self) -> Set[Node]:
        """
        Returns a list of start nodes. A start node is a node that only appears on the left side of an edge
        :return: set of start nodes
        :rtype: Set[Node]
        """
        left_nodes, right_nodes = zip(*list(self))
        return set(left_nodes) - set(right_nodes)

    @property
    def end_nodes(self):
        """
        Returns a list of end nodes. An end node is a node that only appears on the right side of an edge
        :return: set of end nodes
        :rtype: Set[Node]
        """
        left_nodes, right_nodes = zip(*list(self))
        return set(right_nodes) - set(left_nodes)
