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
from copy import deepcopy

from .Graph import DirectedGraph, Node, Cost


class Segment(Node):
    """
    Class use to represent segments in a graph
    """
    def __init__(self, index, speaker, onset, offset, **kwargs):
        """
        Initialisator
        :param index: index of the segment
        :type index: int
        :param speaker: speaker
        :type speaker: str
        :param onset: onset of the segment
        :type onset: int
        :param offset: offset of the segment
        :type offset: int
        :param kwargs: additional arguments the user may use
        :type kwargs: dict
        """
        self._index = index
        self._speaker = speaker
        self._onset = onset
        self._offset = offset

    @property
    def speaker(self):
        """
        Returns the attribute _speaker
        :return: speaker of the segment
        :rtype: str
        """
        return self._speaker

    @property
    def index(self):
        """
        Returns the attribute _index
        :return: index of the segment
        :rtype: int
        """
        return self._index

    @property
    def onset(self):
        """
        Returns the attribute _onset
        :return: onset of the segment
        :rtype: int
        """
        return self._onset

    @property
    def offset(self):
        """
        Returns the attribute _offset
        :return: offset of the segment
        :rtype: int
        """
        return self._offset

    @property
    def duration(self):
        """
        Return the duration of the segment
        :return: duration of the segment
        :rtype: int
        """
        return self.offset - self.onset

    def __str__(self):
        """
        Index of the segment
        :return:
        :rtype:
        """
        return str(self.index)

    def __repr__(self):
        """
        Representation of the segment with it obligatory attributes
        :return:
        :rtype:
        """
        return '<{}: Index {} Speaker {} ({},{}) at {}>'.format(type(self).__name__,
                                                                self.index, self.speaker,
                                                                self.onset, self.offset, hex(id(self)))


class PathCost(Cost):
    """
    Class use to compute the score of a given path
    """
    def __init__(self, segment: Segment) -> None:
        """
        Initialisator
        :param segment: Segment used as first node
        :type segment: Segment
        """
        self._ancestor = segment
        self._speakers = [segment.speaker]
        self._duration = segment.duration
        self._turn_transitions = 0
        self._multi_unit_turn_transitions = 0

    @property
    def num_speakers(self) -> int:
        """
        Returns the number of different speakers for the current path
        :return: length of the speaker set (i.e. number of different speaker in a sequence)
        :rtype: int
        """
        return len(set(self._speakers))

    @property
    def num_segments(self) -> int:
        """
        Return the number of segments for the current path
        :return: number of segments
        :rtype: int
        """
        return len(self._speakers)

    @property
    def num_turns(self) -> int:
        """
        Returns the number of turns in the path
        :return: number of turns
        :rtype: int
        """
        return self.num_segments - 1

    @property
    def num_turn_transitions(self) -> int:
        """
        Returns the number turn transitions (between a speaker and another speaker)
        :return: number of turn transitions
        :rtype: int
        """
        return self._turn_transitions

    @property
    def num_multi_turns_transitions(self)  -> int:
        """
        Returns the number of multi-unit turns (between a speaker and the same speaker)
        :return: number of multi-unit turns
        :rtype: int
        """
        return self._multi_unit_turn_transitions

    @property
    def duration(self):
        """
        Return the total duration of all the segments
        :return: total duration of all the segments
        :rtype: int
        """
        return self._duration

    @property
    def ancestor(self):
        """
        Return the start node
        :return: start node
        :rtype: Segment
        """
        return self._ancestor

    def __add__(self, other: Node):
        """
        Adds a Segment to the current cost
        :param other: segment
        :type other: Segment
        :return: new PathCost object with an updated value
        :rtype: PathCost
        """
        assert isinstance(other, Node), ValueError('Can only add Node (or inherited) to PathCost!')

        # Create fresh copy
        new_cost = deepcopy(self)
        # /!\ use original ancestor as deep copy creates a fresh copy (and thus changes its address) which prevents
        # best path selection to work properly.
        new_cost._ancestor = self._ancestor

        # Add segment information
        new_cost._duration += other.duration
        new_cost._turn_transitions += 1 if other.speaker != new_cost._speakers[-1] else 0
        new_cost._multi_unit_turn_transitions += 1 if other.speaker == new_cost._speakers[-1] else 0
        new_cost._speakers.append(other.speaker)

        return new_cost

    def __repr__(self):
        """
        Returns a representation of the current cost
        :return:
        :rtype:
        """
        return '<{}: \
                    \n\tancestor: {}\
                    \n\tnum_segments: {}\
                    \n\tnum_turns: {}\
                    \n\tnum_turn_transition: {}\
                    \n\tnum_multi_turns_transitions: {}\
                    \n\tnum_speakers: {}\
                    \n\tduration: {} at {}>'.format(type(self).__name__,
                                                    self.ancestor,
                                                    self.num_segments,
                                                    self.num_turns,
                                                    self.num_turn_transitions,
                                                    self.num_multi_turns_transitions,
                                                    self.num_speakers,
                                                    self.duration, hex(id(self)))


class InteractionalSequence(object):
    """
    Class used to store a raw interactional sequence and its best path (if available)
    """
    def __init__(self, interactional_sequence: DirectedGraph) -> None:
        """
        Initialisator
        :param interactional_sequence: a graph representing an interactional sequence
        :type interactional_sequence: DirectedGraph
        """
        super().__init__()

        self._interactional_sequence = interactional_sequence
        self._best_path = None

    def source(self, raw_with_best_path=True) -> str:
        """
        Returns the graphviz source of a graphviz graph
        :param raw_with_best_path: whether the best path be overlaid on the raw graph. If False, only
        the best path will be printed.
        :type raw_with_best_path: bool
        :return: graphviz code for the graph
        :rtype: str
        """
        graph = self._to_graph_viz(raw_with_best_path=raw_with_best_path)
        return graph.source

    def render(self, dirpath, name, format, raw_with_best_path=True, delete_gv=False) -> None:
        """

        :param dirpath: path where the graph should be saved
        :type dirpath: str
        :param name: name of the file
        :type name: str
        :param format: file format used to save the graph (e.g. png, pdf, etc.)
        :type format: str
        :param raw_with_best_path: whether the best path be overlaid on the raw graph. If False, only
        the best path will be printed.
        :type raw_with_best_path: bool
        :param delete_gv:
        :type delete_gv: should the graphviz code be deleted once the graph generated
        :return: None
        :rtype: None
        """
        os.makedirs(dirpath, exist_ok=True)
        full_filepath = os.path.join(dirpath, '{}.gv'.format(name))
        graph = self._to_graph_viz(raw_with_best_path=raw_with_best_path)
        graph.render(filename=full_filepath, format=format)
        if delete_gv:
            os.remove(full_filepath)

    def _to_graph_viz(self, raw_with_best_path=True):
        """
        Generates the graph for the given interactional sequence. If no best path exists, the raw interaction
        graph is plotted. If the best path exists, only the best path will be printed. To print the raw interactional
        sequence along with the best path, use `raw_with_best_path=True`
        :param raw_with_best_path: whether the best path be overlaid on the raw graph. If False, only
        the best path will be printed.
        :type raw_with_best_path: bool
        :return: graphviz Digraph object
        :rtype: graphviz.Digraph
        """
        from .graph_visualisation import generate_interactional_sequence_visualisation
        if raw_with_best_path and self._best_path:
            return generate_interactional_sequence_visualisation(list(self._interactional_sequence),
                                                                 highlight_edges=list(self._best_path))
        else:
            return generate_interactional_sequence_visualisation(list(self))

    def __getitem__(self, index):
        return list(self.__iter__())[index]

    def __len__(self):
        return len(list(self.__iter__()))

    def __iter__(self):
        """
        Iterated over the edged of the graph. If a best path exists, the iteration will be done over the edges of the
        best path, if not, the iteration will be done over the edges of the raw interactional sequence.
        :return:
        :rtype:
        """
        if self._best_path:
            return iter(self._best_path)
        else:
            return iter(self._interactional_sequence)
