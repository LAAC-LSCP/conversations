#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: consts.py (as part of project conversations)
#   Created: 29/06/2022 10:17
#   Last Modified: 29/06/2022 10:17
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


from enum import Enum


class MODE(Enum):
    """
    Enumeration of the existing modes available to the user
    """
    ALL = 'all'

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, Enum):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)


class SPK(Enum):
    """
    Enumeration of the speaker types used in ChildProject
    """
    CHI = "CHI"
    FEM = "FEM"
    MAL = "MAL"
    OTH = "OTH"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, Enum):
            return self.value == other.value
        return False

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.value)
