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
from itertools import chain, repeat
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
        self.adjacency.setdefault(node1, dict()) # change to dict to be able to weight edges
        self.adjacency.setdefault(node2, dict())

        self.adjacency[node1].setdefault('prev', dict())
        self.adjacency[node1].setdefault('next', list())
        self.adjacency[node2].setdefault('prev', dict())
        self.adjacency[node2].setdefault('next', list())

        self.adjacency[node1]['next'].append(node2)
        #self.adjacency[node2]['prev'][node1] = {}  # Will be used to store path costs

    @property
    def statistics(self) -> dict:
        return {'num_edges': self.num_edges,
                'num_nodes': self.num_nodes}

    @property
    def num_edges(self) -> int:
        return len(list(self))

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
            connected_nodes = self.adjacency[candidate_node]['next']

            next_node_pairs = list(zip(repeat(candidate_node, len(connected_nodes)), connected_nodes))
            next_nodes_to_visit = next_node_pairs

            transition = []
            while next_nodes_to_visit:
                node_pair = next_nodes_to_visit.pop()
                candidate_node, connected_node = node_pair

                if node_pair in visited_pairs: continue
                visited_pairs.add(node_pair)
                if not connected_node: continue

                if self._apply_transition_rules(candidate_node, connected_node, **kwargs):
                    transition.append(node_pair)
                    connected_nodes = self.adjacency[connected_node]['next']
                    candidate_node = connected_node
                    next_node_pairs = list(zip(repeat(candidate_node, len(connected_nodes)), connected_nodes))
                    next_nodes_to_visit.extend(next_node_pairs)

            if transition:
                chain_sequences.append(transition)

        # Some components might still be disconnected when they shouldn't. If so, merge them.
        # This situation happens when one start node is connected to a node that already belongs to another chain
        to_skip = set()
        for i_t1 in range(len(chain_sequences)):
            if i_t1 in to_skip: continue
            t1_flat = set(chain(*chain_sequences[i_t1]))
            for i_t2 in range(i_t1 + 1, len(chain_sequences)):
                t2_flat = set(chain(*chain_sequences[i_t2]))

                # Two chains are connected if their share one node
                if len(t1_flat.intersection(t2_flat)):
                    chain_sequences[i_t1] = chain_sequences[i_t1] + chain_sequences[i_t2]
                    to_skip.add(i_t2)

        # Transform chain sequences to graph
        chain_sequences = [DirectedGraph.from_tuple_list(item)
                           for idx, item in enumerate(chain_sequences) if idx not in to_skip]

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
        queue = [[[start_node], set([start_node])]]

        while queue:
            (tmp_path, node_set) = queue.pop()
            last_node = tmp_path[-1]

            if last_node == end_node:
                paths.append(DirectedGraph.from_tuple_list(pairwise(tmp_path)))

            for link_node in self.adjacency[last_node]['next']:
                if link_node not in node_set:
                    set_update = node_set.copy()
                    set_update.add(link_node)

                    new_path = [tmp_path + [link_node], set_update]
                    queue.append(new_path)

        return paths

    def compute_path_cost(self, cost_counter, start_node, compare):
        # Remember which nodes we visited
        visited_pairs = set()

        # Initialise cost_counter from the specified starting node
        node_pair_cost = cost_counter(start_node)

        # Get connected nodes
        incoming_node = start_node
        outgoing_nodes = self.adjacency[incoming_node]['next']

        # For each of the connected nodes, add it to the current cost_counter
        next_node_pairs = []
        for outgoing_node in outgoing_nodes:
            outgoing_node_cost = node_pair_cost + outgoing_node

            # Add cost (or swap)
            current_path_cost, _ = self.adjacency[outgoing_node]['prev'].setdefault(outgoing_node_cost.ancestor, (outgoing_node_cost, incoming_node))
            current_path_cost = compare([current_path_cost, outgoing_node_cost])
            self.adjacency[outgoing_node]['prev'][outgoing_node_cost.ancestor] = (current_path_cost, incoming_node)

            next_node_pairs.append((incoming_node, outgoing_node))
        next_nodes_to_visit = next_node_pairs

        # For the next node pair to visit
        while next_nodes_to_visit:
            # Get pair and continue or skip
            node_pair = next_nodes_to_visit.pop(0)  # /!\ important to pop the first item and not the last
                                                    #     so as not do go in depth but in breadth!
            incoming_node, outgoing_node = node_pair
            if node_pair in visited_pairs: continue

            # Mark visited
            visited_pairs.add(node_pair)

            # Get costs
            previous_costs = self.adjacency[outgoing_node]['prev'].values()

            # Get outgoing nodes from the outgoing node
            outgoing_nodes = self.adjacency[outgoing_node]['next']

            incoming_node = outgoing_node
            next_node_pairs = []
            for outgoing_node in outgoing_nodes:
                next_node_pairs.append((incoming_node, outgoing_node))
                for (previous_cost, _) in previous_costs:
                    outgoing_node_cost = previous_cost + outgoing_node

                    prev_path_cost, prev_path_incoming = self.adjacency[outgoing_node]['prev'].setdefault(outgoing_node_cost.ancestor,
                                                                                         (None, None))
                    current_path_cost = compare([prev_path_cost, outgoing_node_cost]) if prev_path_cost else outgoing_node_cost
                    #print(incoming_node, outgoing_node, (outgoing_node_cost, incoming_node), (prev_path_cost, prev_path_incoming), current_path_cost)
                    self.adjacency[outgoing_node]['prev'][outgoing_node_cost.ancestor] = (current_path_cost, prev_path_incoming if current_path_cost == prev_path_cost else incoming_node)
            next_nodes_to_visit.extend(next_node_pairs)

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
            print("{} {} -> {}".format(type(key), str(key), list(map(str, self.adjacency[key]['next']))))

    def __iter__(self) -> Optional[Tuple[Node, Node]]:
        """
        Create an iterator to go through the edge adjacencies
        :return: 2-tuple of Nodes or None
        :rtype: Optional[Tuple[Node, Node]]
        """
        for input_node in self.adjacency:
            for output_node in self.adjacency[input_node]['next']:
                yield input_node, output_node
        return

    def __neg__(self):
        edges = list(self)
        reversed_edges = [(b,a) for (a, b) in edges]

        return DirectedGraph.from_tuple_list(reversed_edges)