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

def default_turn_transition_rules(candidate_node, connected_node, **kwargs):
    tgt_participant = kwargs.get('target_participant', None)
    interactants = kwargs.get('interactants', None)
    allow_multi_unit_turns = kwargs.get('allow_multi_unit_turns', False)
    allow_interactions_btw_interactants = kwargs.get('allow_interactions_btw_interactants', False)

    assert tgt_participant, ValueError('Missing target participant!')

    # Rules
    if interactants:
        if candidate_node.speaker == tgt_participant and connected_node.speaker in interactants:
            return True
        if candidate_node.speaker in interactants and connected_node.speaker == tgt_participant:
            return True
        if allow_interactions_btw_interactants:
            if candidate_node.speaker in interactants and connected_node.speaker in interactants and \
                    candidate_node.speaker != connected_node.speaker:
                # Will require filtering to remove chains that do not include tgt_participant
                return True
    else:
        if candidate_node.speaker == tgt_participant or connected_node.speaker == tgt_participant:
            return True

    if allow_multi_unit_turns:
        # Will require filtering to remove chains that do not include tgt_participant
        if candidate_node.speaker == connected_node.speaker:
            return True

    return False


def default_filtering_rules(chain_sequences, **kwargs):
    tgt_participant = kwargs.get('target_participant', None)
    assert tgt_participant, ValueError('Missing target participant!')

    # If allow_multi_unit_turns, filter out chains that do not include the tgt_participant
    chain_sequences = list(filter(
        lambda turns: any([segment.speaker == tgt_participant for segment in chain(*turns)]), chain_sequences))


    return chain_sequences


def default_path_selection_rules(list_of_path, **kwargs):
    sorted_path = sorted(list_of_path,
                         key = lambda path: path.stats()['num_turns'],
                         reverse=True)
    return sorted_path[0]


def default_statistics(statistics, edges, **kwargs):
    statistics = {}

    speakers, durations = zip(*[(segment.speaker, segment.duration) for segment in set(flatten(edges))])
    statistics['num_speakers'] = len(set(speakers))
    statistics['num_turns'] = len(edges)
    statistics['num_segments'] = len(durations)
    statistics['total_duration'] = sum(durations)

    return statistics
