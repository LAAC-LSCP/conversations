#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: InteractionalSequence.py (as part of project conversations)
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

from .Graph import DirectedGraph

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
        if self._best_path:
            return len(self._best_path)
        else:
            return len(self._interactional_sequence)

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
