#!usr/bin/env python
# -*- coding: utf8 -*-
#
# -----------------------------------------------------------------------------
#   File: Cost.py (as part of project conversations)
#   Created: 21/03/2023 14:13
#   Last Modified: 21/03/2023 14:13
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

from conversations.graph.base.Node import Node


class Cost(abc.ABC):
    """
    Abstract class used to compute costs in a graph
    """
    def __init__(self, ancestor):
        self._ancestor = ancestor

    @abc.abstractmethod
    def __add__(self, other: Node):
        pass

    @property
    def ancestor(self) -> Node:
        """
        Represents the start node of the path we compute the cost of
        :return: start node
        :rtype: Node
        """
        return self._ancestor