#!usr/bin/env python
#-*- coding: utf8 -*-
#
# -----------------------------------------------------------------------------
#   File: Segment.py (as part of project conversations)
#   Created: 14/12/2022 16:13
#   Last Modified: 14/12/2022 16:13
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

from conversations.Graph import Node

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
