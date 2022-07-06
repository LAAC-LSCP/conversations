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

import os
from typing import List

from .Graph import DirectedGraph, Node
from .graph_visualisation import generate_interactional_sequence_visualisation


class Segment(Node):
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


class InteractionGraph(DirectedGraph):
    def __init__(self, segments: List[Segment]):
        super().__init__(nodes=segments)

    @staticmethod
    def source(interactional_sequence):
        graph = InteractionGraph._build_graphviz_visualisation(interactional_sequence)
        return graph.source

    @staticmethod
    def render(interactional_sequence, dirpath, name, format):
        full_filepath = os.path.join(dirpath, '{}.gv'.format(name))
        graph = InteractionGraph._build_graphviz_visualisation(interactional_sequence)
        graph.render(filename=full_filepath, format=format)
        os.remove(full_filepath)

    @staticmethod
    def _build_graphviz_visualisation(interactional_sequence):
        return generate_interactional_sequence_visualisation(interactional_sequence)