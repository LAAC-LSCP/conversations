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
from .utils import flatten


def default_turn_transition_rules(candidate_node, connected_node,  # Obligatory argument
                                  target_participant,              # User-defined obligatory argument
                                  interactants = None, allow_multi_unit_turns = False,  # Optional arguments
                                  allow_interactions_btw_interactants = False, **kwargs):
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

        if allow_interactions_btw_interactants:
            return True

    if allow_multi_unit_turns:
        # Will require filtering to remove chains that do not include tgt_participant
        if candidate_node.speaker == connected_node.speaker:
            return True

    return False


def default_filtering_rules(chain_sequences, target_participant, **kwargs):
    # If allow_multi_unit_turns, filter out chains that do not include the tgt_participant
    chain_sequences = list(filter(
        lambda turns: any([segment.speaker == target_participant for segment in chain(*turns)]), chain_sequences))

    return chain_sequences


def default_path_selection_rules(list_of_path, **kwargs):
    sorted_path = sorted(list_of_path,
                         key=lambda path: path.statistics['num_turns'],
                         reverse=True)
    best_path = sorted_path[0]

    return best_path


def default_statistics(statistics, edges):
    statistics = {}

    speakers, durations = zip(*[(segment.speaker, segment.duration) for segment in set(flatten(edges))])
    statistics['num_speakers'] = len(set(speakers))
    statistics['num_turns'] = len(edges)
    statistics['num_segments'] = len(durations)
    statistics['total_duration'] = sum(durations)

    return statistics
