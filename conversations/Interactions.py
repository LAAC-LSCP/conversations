#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: Interactions.py (as part of project conversations)
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

import os
from typing import Callable, Optional

from .Graph import DirectedGraph, Node, Cost
from .graph_visualisation import generate_interactional_sequence_visualisation


class PathCost(Cost):
    def __init__(self, segment):
        self._ancestor = segment
        self._speakers = [segment.speaker]
        self._duration = segment.duration

    @property
    def num_speakers(self):
        return len(set(self._speakers))

    @property
    def num_segments(self):
        return len(self._speakers)

    @property
    def num_turns(self):
        return self.num_segments - 1

    @property
    def duration(self):
        return self._duration

    @property
    def ancestor(self):
        return self._ancestor

    def __add__(self, other: Node):
        assert isinstance(other, Node), ValueError('Can only add Node (or inherited) to PathCost!')

        # Create fresh copy
        new_cost = PathCost(self._ancestor)
        # Copy old information
        new_cost._speakers = self._speakers.copy()
        new_cost._duration = self._duration

        # Add segment information
        new_cost._speakers.append(other.speaker)
        new_cost._duration += other.duration

        return new_cost

    def __repr__(self):
        return '<{}: \
                    \n\tancestor: {}\
                    \n\tnum_segments: {}\
                    \n\tnum_turns: {}\
                    \n\tnum_speakers: {}\
                    \n\tduration: {} at {}>'.format(type(self).__name__,
                                             self.ancestor,
                                             self.num_segments,
                                             self.num_turns,
                                             self.num_speakers,
                                             self.duration, hex(id(self)))


class Segment(Node):
    def __init__(self, index, speaker, onset, offset, **kwargs):
        self._index = index
        self._speaker = speaker
        self._onset = onset
        self._offset = offset

    @property
    def speaker(self):
        return self._speaker

    @property
    def index(self):
        return self._index

    @property
    def onset(self):
        return self._onset

    @property
    def offset(self):
        return self._offset

    @property
    def duration(self):
        return self.offset - self.onset

    def __str__(self):
        return str(self.index)

    def __repr__(self):
        return '<{}: Index {} Speaker {} ({},{}) at {}>'.format(type(self).__name__,
                                                                self.index, self.speaker,
                                                                self.onset, self.offset, hex(id(self)))

class InteractionalSequence(object):
    # store best path (if it exists) and return that one by default
    def __init__(self, interactional_sequence: DirectedGraph, stat_rules: Optional[Callable] = None):
        super().__init__()

        self._interactional_sequence = interactional_sequence
        self._stats_rules = stat_rules
        self._best_path = None

    @property
    def statistics(self) -> dict:
        statistics = self._best_path.statistics if self._best_path else self._interactional_sequence.statistics

        if self._stats_rules:
            edges = list(self)
            statistics = self._stats_rules(statistics=statistics, edges=edges)
        return statistics

    def source(self, raw_with_best_path=True):
        graph = self._to_graph_viz()
        return graph.source

    def render(self, dirpath, name, format, raw_with_best_path=True, delete_gv=False):
        full_filepath = os.path.join(dirpath, '{}.gv'.format(name))
        graph = self._to_graph_viz()
        graph.render(filename=full_filepath, format=format)
        if delete_gv:
            os.remove(full_filepath)

    def _to_graph_viz(self, raw_with_best_path=True):
        if raw_with_best_path:
            return generate_interactional_sequence_visualisation(list(self._interactional_sequence),
                                                                 highlight_edges= list(self._best_path))
        else:
            return generate_interactional_sequence_visualisation(list(self))

    def __iter__(self):
        if self._best_path:
            return iter(self._best_path)
        else:
            return iter(self._interactional_sequence)
