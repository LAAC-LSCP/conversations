#!usr/bin/env python
# -*- coding: utf8 -*-
from copy import deepcopy
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


def pairwise(iterable: Iterable) -> Iterable:
    """
    Returns an iterable with consecutive elements paired together (2-gram)
    [a, b, c, d, e] -> [(a, b), (b, c), (c, d), (d, e)]
    :param iterable: iterable
    :type iterable: Iterable
    :return: Iterable
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def overlap(onset: float, offset: float, target_onset: float, target_offset: float) -> float:
    """
    Returns the amount of overlap between a segment starting at onset and finishing at offset and another
    segment starting at target_onset and finishing at target_offset
    :param onset: onset of the first segment
    :type onset: float
    :param offset: offset of the second segment
    :type offset: float
    :param target_onset: onset of the second segment
    :type target_onset: float
    :param target_offset: offset of the second segment
    :type target_offset: float
    :return: Amount of overlap
    :rtype: float
    """
    return max(0, min(offset, target_offset) - max(onset, target_onset))


def overlaps(onset: float, offset: float, target_onset: float, target_offset: float) -> bool:
    """
    Returns whether a segment starting at onset and finishing at offset and another
    segment starting at target_onset and finishing at target_offset overlap
    :param onset: onset of the first segment
    :type onset: float
    :param offset: offset of the second segment
    :type offset: float
    :param target_onset: onset of the second segment
    :type target_onset: float
    :param target_offset: offset of the second segment
    :type target_offset: float
    :return: Amount of overlap
    :rtype: boolean
    """
    return bool(overlap(onset, offset, target_onset, target_offset))


def flatten(iterable: Iterable) -> list:
    """
    Flattens an iterable
    [['a', 'b'], ['c', 'd']] -> ['a', 'b', 'c', 'd']
    :param iterable: iterable
    :type iterable: Iterable
    :return: flattened iterable
    :rtype: list
    """
    R = []
    L = deepcopy(iterable)
    while L:
        item = L.pop()
        if isinstance(item, list):
            L.extend(item)
        else:
            R.append(item)
    return R[::-1]
