#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: InteractionGraph.py (as part of project conversations)
#   Created: 15/06/2022 13:44
#   Last Modified: 15/06/2022 13:44
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

from itertools import repeat
from typing import Callable, List, Tuple, Union


class Segment(object):
    def __init__(self, index, speaker, onset, offset):
        self.index = index
        self.speaker = speaker
        self.onset = onset
        self.offset = offset

    def __str__(self):
        return str(self.index)

    def __repr__(self):
        return '<{}: Index {} Speaker {} ({},{}) at {}>'.format(type(self).__name__, self.index, self.speaker,
                                                                 self.onset, self.offset, hex(id(self)))


class InteractionGraph(object):

    def __init__(self, segments: List[Segment]) -> None:
        self.nodes = segments
        self.adjacency = {node: set() for node in self.nodes}

        self._transition_rules = lambda candidate_node, connected_node, **kwargs: True
        self._filtering_rules = lambda chain_sequences, **kwargs: chain_sequences

    def add_edge(self, node1:Segment, node2: Segment) -> None:
        self.adjacency[node1].add(node2)

    @property
    def transition_rules(self) -> Callable:
        return self._transition_rules

    @transition_rules.setter
    def transition_rules(self, transition_rules: Callable) -> None:
        self._transition_rules = transition_rules

    @property
    def filtering_rules(self) -> Union[Callable, None]:
        return self._filtering_rules

    @filtering_rules.setter
    def filtering_rules(self, filtering_rules: Union[Callable, None]) -> None:
        self._filtering_rules = filtering_rules

    def get_chains(self, **kwargs) -> List[List[Tuple[Segment]]]:
        chain_sequences = [] # Interactional sequences

        visited_pairs = set()
        for node in self.adjacency.keys():
            candidate_node = node
            connected_nodes = self.adjacency[candidate_node]

            next_node_pairs = list(zip(repeat(candidate_node, len(connected_nodes)), connected_nodes))
            next_nodes_to_visit = next_node_pairs

            transition = [] # Conversational turn
            while(next_nodes_to_visit):
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
                chain_sequences.append(transition)

        return self._apply_filtering_rules(chain_sequences, **kwargs)


    def _apply_filtering_rules(self, chain_sequences: List[List[Tuple[Segment]]], **kwargs) -> List[List[Tuple[Segment]]]:
        assert callable(self._filtering_rules), \
            ValueError('Filtering rules were not set properly or are not callable!')
        return self._filtering_rules(chain_sequences = chain_sequences, **kwargs)


    def _apply_transition_rules(self, candidate_node: Segment, connected_node: Segment, **kwargs):
        assert callable(self._transition_rules), \
            ValueError('Transition rules were not set properly or are not callable!')
        return self._transition_rules(candidate_node=candidate_node, connected_node= connected_node, **kwargs)


    def print_adjacencies(self) -> None:
        for key in self.adjacency.keys():
            print("Segment {} -> {}".format(str(key), map(str, self.adjacency[key])))