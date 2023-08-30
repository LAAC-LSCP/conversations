#!usr/bin/env python
# -*- coding: utf8 -*-
#
# -----------------------------------------------------------------------------
#   File: ConvCost.py (as part of project conversations)
#   Created: 14/12/2022 16:14
#   Last Modified: 14/12/2022 16:14
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

from copy import deepcopy
from functools import wraps

from conversations.graph.base.Cost import Cost
from conversations.graph.base.Node import Node
from conversations.graph.conv.Segment import Segment

costs = {}

def register_cost(*args, **kwargs):
    def decorated(cls):
        costs[cls.__name__] = cls

        @wraps(cls)
        def wrapper():
            return cls(*args, **kwargs)
        return wrapper
    return decorated

@register_cost
class ConvCost(Cost):
    """
    Class use to compute the score of a given path
    """
    def __init__(self, segment: Segment) -> None:
        """
        Initialisator
        :param segment: Segment used as first node
        :type segment: Segment
        """
        super(ConvCost, self).__init__(segment)

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
        :rtype: ConvCost
        """
        assert isinstance(other, Node), ValueError('Can only add Node (or inherited) to ConvCost!')

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
