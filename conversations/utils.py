#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: utils.py (as part of project conversations)
#   Created: 15/06/2022 17:37
#   Last Modified: 15/06/2022 17:37
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
#       • Utility functions
# -----------------------------------------------------------------------------

from typing import Iterable

from itertools import chain, tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def overlaps(onset, offset, target_onset, target_offset):
    return bool(max(0, min(offset, target_offset) - max(onset, target_onset)))

def flatten(iterable: Iterable) -> list:
    """
    Flattens the input iterable [['a', 'b'], ['c', 'd']] -> ['a', 'b', 'c', 'd']
    :param iterable: iterable
    :type iterable: Iterable
    :return: flattened iterable
    :rtype: list
    """
    return list(chain(*iterable))