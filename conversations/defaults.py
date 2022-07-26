#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: defaults.py (as part of project conversations)
#   Created: 08/07/2022 11:18
#   Last Modified: 08/07/2022 11:18
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


from itertools import chain
from operator import attrgetter
from typing import List, Optional

from .Graph import Cost, Node
from .Interactions import InteractionalSequence
from .utils import flatten


def default_turn_transition_rules(candidate_node: Node, connected_node: Node,  # Obligatory argument
                                  target_participant: str,              # User-defined obligatory argument
                                  interactants: Optional[List[str]] = None, allow_multi_unit_turns: bool = False,  # Optional arguments
                                  allow_interactions_btw_interactants: bool = False, **kwargs) -> bool:
    """
    Returns whether the candidate node and the connected node should be considered as really connected or not.
    /!\ The names `candidate_node` and `connected_node` are fixed and cannot be changed!
    ---- Obligatory arguments ----
    :param candidate_node: candidate segment
    :type candidate_node: Segment
    :param connected_node: connected segment
    :type connected_node: Segment
    ---- User-defined arguments----
    :param target_participant: which speaker should be considered the target participant
    :type target_participant: str
    :param interactants: interactants to consider
    :type interactants: List[str]
    :param allow_multi_unit_turns: whether multi-turns unit be allowed
    :type allow_multi_unit_turns: bool
    :param allow_interactions_btw_interactants: whether interactants are allowed to interact between one another
    :type allow_interactions_btw_interactants: bool
    :param kwargs: other user-defined keyword arguments not used in this function
    :type kwargs: dict
    :return: whether two segments should be considered connected or not
    :rtype: bool
    """
    # Rules
    if interactants:
        if candidate_node.speaker == target_participant and connected_node.speaker in interactants:
            return True
        if candidate_node.speaker in interactants and connected_node.speaker == target_participant:
            return True
        if allow_interactions_btw_interactants:
            if candidate_node.speaker in interactants and connected_node.speaker in interactants and \
                    candidate_node.speaker != connected_node.speaker:
                # Will require filtering to remove chains that do not include tgt_participant
                return True
    else:
        if candidate_node.speaker == target_participant or connected_node.speaker == target_participant:
            return True

        # Allow interactions between everyone
        if allow_interactions_btw_interactants:
            return True

    if allow_multi_unit_turns:
        # Will require filtering to remove chains that do not include tgt_participant
        if candidate_node.speaker == connected_node.speaker:
            return True

    return False


def default_filtering_rules(chain_sequences: List[InteractionalSequence], target_participant: str, **kwargs):
    """
    Filtering rule to exclude interactional sequences based on their properties
    :param chain_sequences: list of interactional sequences
    :type chain_sequences: List[InteractionalSequence]
    :param target_participant: which speaker should be considered the target participant
    :type target_participant: str
    :param kwargs: other user-defined keyword arguments not used in this function
    :type kwargs: dict
    :return: list of interactional sequences with non-valid sequences removed
    :rtype: List[InteractionalSequence]
    """
    # If allow_multi_unit_turns, filter out chains that do not include the tgt_participant
    chain_sequences = list(filter(
        lambda turns: any([segment.speaker == target_participant for segment in chain(*turns)]), chain_sequences))

    return chain_sequences


def default_path_selection_rules(path_list: List[Cost], selection_key: List[str], **kwargs):
    """
    Sorts a list of Cost and return the best
    :param path_list: list of costs
    :type path_list: Cost
    :param kwargs: other user-defined keyword arguments not used in this function
    :type kwargs: dict
    :return: best cost (as defined by the sorting function and the keys used)
    :rtype: Cost
    """
    return sorted(path_list, reverse=True, key=attrgetter(*selection_key))[0]
