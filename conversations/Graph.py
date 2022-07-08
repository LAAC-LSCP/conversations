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
from itertools import repeat
from typing import Callable, List, Tuple, Set, Dict, Optional

from .utils import pairwise


class Node(abc.ABC):

    @abc.abstractmethod
    def __init__(self):
        pass


class Graph(abc.ABC):

    @abc.abstractmethod
    def __init__(self):
        pass


class DirectedGraph(Graph):

    def __init__(self, transition_rules: Optional[Callable] = None) -> None:
        # Stores nodes and edges
        self.adjacency = dict()

        # Define transition rules to go from one node to another
        # By default, transitions are allowed from any node to another linked by and edge
        self._transition_rules = lambda candidate_node, connected_node, **kwargs: True

        if transition_rules:
            self.transition_rules = transition_rules

    @classmethod
    def from_tuple_list(cls, tuple_list: List[Tuple[Node, Node]]):
        """
        Create a graph from a list of edges between nodes given as 2-tuple (start_node, end_node)
        :param tuple_list: list of tuples
        :type tuple_list: List[Tuple[Node, Node]]
        :return: a graph
        :rtype: DirectedGraph
        """
        graph = cls()
        for node_tuple in tuple_list:
            graph.add_edge(*node_tuple)
        return graph

    def add_edge(self, node1: Node, node2: Node) -> None:
        """
        Create an edge between two nodes
        :param node1: input node
        :type node1: Node
        :param node2: output node
        :type node2: Node
        :return: None
        :rtype: None
        """
        self.adjacency.setdefault(node1, set())
        self.adjacency.setdefault(node2, set())
        self.adjacency[node1].add(node2)

    def stats(self) -> dict:
        return {'num_edges': self.num_edges,
                'num_nodes': self.num_nodes}

    @property
    def num_edges(self) -> int:
        return sum(map(len, self.adjacency.values()))

    @property
    def num_nodes(self) -> int:
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

    @property
    def transition_rules(self) -> Callable:
        """
        Returns the transitions rules used.
        :return: Function containing the transition rules
        :rtype: Callable
        """
        return self._transition_rules

    @transition_rules.setter
    def transition_rules(self, transition_rules: Callable) -> None:
        """
        Sets the transition rules
        :param transition_rules: A function containing the transition rules to apply
        :type transition_rules: Callable
        :return: None
        :rtype: None
        """
        assert callable(self.transition_rules), \
            ValueError('Transition rules were not set properly or are not callable!')
        self._transition_rules = transition_rules

    def get_connected_components(self, **kwargs: Dict) -> List[Graph]:
        """

        :param kwargs: dictionary of attributes/values
        :type kwargs: dict
        :return: list of connected components as DirectedGraph
        :rtype: List['DirectedGraph']
        """
        chain_sequences = []

        visited_pairs = set()
        for node in self.adjacency.keys():
            candidate_node = node
            connected_nodes = self.adjacency[candidate_node]

            next_node_pairs = list(zip(repeat(candidate_node, len(connected_nodes)), connected_nodes))
            next_nodes_to_visit = next_node_pairs

            transition = []
            while next_nodes_to_visit:
                node_pair = next_nodes_to_visit.pop()
                candidate_node, connected_node = node_pair

                if node_pair in visited_pairs: continue
                if connected_node == set(): continue

                visited_pairs.add(node_pair)

                if self._apply_transition_rules(candidate_node, connected_node, **kwargs):
                    transition.append(node_pair)
                    connected_nodes = self.adjacency[connected_node]
                    candidate_node = connected_node
                    next_node_pairs = list(zip(repeat(candidate_node, len(connected_nodes)), connected_nodes))
                    next_nodes_to_visit.extend(next_node_pairs)

            if transition:
                chain_sequences.append(DirectedGraph.from_tuple_list(transition))

        return chain_sequences

    def get_all_paths(self):
        paths = []
        for start_node in self.start_nodes:
            for end_node in self.end_nodes:
                paths.extend(self.get_paths(start_node, end_node))
        return paths

    def get_paths(self, start_node: Node, end_node: Node) -> List[Graph]:
        """
        Returns all the paths from one node to another
        :param start_node: Node where to start graph exploration
        :type start_node: Node
        :param end_node: Node where to end graph exploration
        :type end_node: Node
        :return: list of DirectedGraph
        :rtype:  List['DirectedGraph']
        """
        paths = []

        queue = [[start_node]]
        while queue:
            tmp_path = queue.pop()
            last_node = tmp_path[-1]

            if last_node == end_node:
                paths.append(tmp_path.copy())

            for link_node in self.adjacency[last_node]:
                if link_node not in tmp_path:
                    new_path = tmp_path + [link_node]
                    queue.append(new_path)

        paths = [DirectedGraph.from_tuple_list(pairwise(path)) for path in paths]
        return paths

    def _apply_transition_rules(self, candidate_node: Node, connected_node: Node, **kwargs: dict) -> bool:
        """
        Apply the transition rules from one node to another
        :param candidate_node: input node
        :type candidate_node: Node
        :param connected_node: output node
        :type connected_node: Node
        :param kwargs: dict of attributes/values pairs
        :type kwargs: dict
        :return: whether it is possible to go to connected_node from candidate_node
        :rtype: bool
        """
        return self._transition_rules(candidate_node=candidate_node, connected_node=connected_node, **kwargs)

    def print_adjacencies(self) -> None:
        """
        Prints the adjacencies declared in the graph
        :return: None
        :rtype: None
        """
        for key in self.adjacency.keys():
            print("{} {} -> {}".format(type(key), str(key), map(str, self.adjacency[key])))

    def __iter__(self) -> Optional[Tuple[Node, Node]]:
        """
        Create an iterator to go through the edge adjacencies
        :return: 2-tuple of Nodes or None
        :rtype: Optional[Tuple[Node, Node]]
        """
        for input_node in self.adjacency:
            for output_node in self.adjacency[input_node]:
                yield input_node, output_node
        return
