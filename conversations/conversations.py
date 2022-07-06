#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: conversations.py (as part of project conversations)
#   Created: 03/06/2022 17:13
#   Last Modified: 03/06/2022 17:13
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
from itertools import chain
from typing import List, Union, Callable, Optional

import pandas as pd
pd.options.display.max_rows = 500
pd.options.display.min_rows = 500

from .InteractionGraph import InteractionGraph, Segment
from .graph_visualisation import generate_interactional_sequence_visualisation
from .consts import SPK, MODE
from .utils import flatten, overlaps


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


def default_filter_interactional_sequences(chain_sequences, **kwargs):
    tgt_participant = kwargs.get('target_participant', None)
    assert tgt_participant, ValueError('Missing target participant!')

    # If allow_multi_unit_turns, filter out chains that do not include the tgt_participant
    chain_sequences = list(filter(
        lambda turns: any([segment.speaker == tgt_participant for segment in chain(*turns)]), chain_sequences))


    return chain_sequences


def interactional_sequences(segments: pd.DataFrame,
                            # Participants
                            target_participant: Union[SPK, str],
                            interactants:Optional[Union[List[str], List[SPK]]] = None,
                            # Segment connectivity
                            allowed_gap: int = 1000, allowed_overlap:int =0,
                            allow_segment_jump: bool = False,
                            # Filtering
                            min_utt_dur: int = 0, max_utt_dur:int = 0,
                            lx_only:Union[bool, str] = False, lx_col: Union[None, str] = None,
                            # Transitions and filtering rules
                            turn_transition_rules: Callable = default_turn_transition_rules,
                            filter_interactional_sequences: Callable = default_filter_interactional_sequences,
                            # Parameters used by the default transition/filtering rules
                            allow_multi_unit_turns:bool = False,
                            allow_interactions_btw_interactants: bool = False,
                            mode: Union[MODE, str] = MODE.ALL,):

    if allowed_overlap: raise NotImplementedError
    if mode != MODE.ALL: raise NotImplementedError

    # A couple of assertion to make sure everything is right
    assert abs(allowed_gap) == allowed_gap, ValueError('allowed_gap should be positive!')
    assert abs(allowed_overlap) == allowed_overlap, ValueError('allowed_overlap should be positive!')
    assert abs(min_utt_dur) == min_utt_dur, ValueError('min_utt_dur should be positive!')
    assert abs(max_utt_dur) == max_utt_dur, ValueError('max_utt_dur should be positive!')
    assert mode in MODE, ValueError('Mode should be one of ({})!'.format('/'.join([item.value for item in MODE])))

    # Get annotations for a given set
    segments.index.name = 'index'

    # These columns will be filled later
    segments['inter_seq_index'], segments['conv_turn_index'] = '', ''

    #
    #   FILTERING
    #

    # Remove segments based on duration
    segments['segment_duration'] = (segments['segment_offset'] - segments['segment_onset'])
    segments = segments[segments['segment_duration'] > min_utt_dur]
    segments = segments[segments['segment_duration'] < max_utt_dur] if max_utt_dur > 0 else segments

    # Remove segments based on their linguistic type
    if lx_only:
        # /!\ Warning: experimental!
        assert lx_col and type(lx_only) != str, \
            ValueError('Specify which column should be used to assert linguitic type using lx_col parameter.')
        lx_re = lx_only if type(lx_only) == str else r'^(?:(?!(J|Y)).)*$' # Remove VCM cries and junk
        segments = segments[segments[lx_col].fillna('').str.match(lx_re)]

    #
    #   Build list of nodes and their connections
    #

    # Build list of nodes
    segments['node'] = segments.apply(axis=1, func= lambda row: \
            Segment(index=row.name, speaker=row['speaker_type'],
                    onset=row['segment_onset'], offset=row['segment_offset']))

    # For each nodes, get connected nodes
    segments['connected_nodes'] = segments.apply(axis=1,
            func= lambda t_row: segments[
                segments.apply(axis=1,
                                  # Get overlapping segments
                    func=lambda c_row: (overlaps(c_row['segment_onset'], c_row['segment_offset'],
                                            t_row['segment_onset'], t_row['segment_offset'] + allowed_gap))
                                  and c_row['segment_onset'] >= t_row['segment_onset'] # only look after
                                  # Remove identical segments
                                  and t_row.name != c_row.name)
            ])

    if not allow_segment_jump:
        # Timeline  | t = t0 <-------------------------------------> t = t0 + allowed_gap
        # Target    |            |----------|
        # Candidate |               |---Keep---| |--Remove--|
        segments['connected_nodes'] = segments['connected_nodes'].apply(
            func = lambda df: (df.groupby('speaker_type')
                            # Keep only the first segment for each candidate speaker
                            .apply(lambda rows: (rows.sort_values(by='segment_onset', ascending=True)
                                                .head(n=1)))
                            # Remove multi-indexing and keep original index
                            .apply(lambda rows: rows if not rows.index.nlevels > 1
                                                else rows.droplevel(0))))

    # Retrieve indexes of connected nodes
    segments['connected_nodes'] = segments['connected_nodes'].apply(lambda df: df.index)

    #
    #   Build and populate graph
    #

    # Build Graph
    interaction_graph = InteractionGraph(segments=list(segments['node']))

    # Populate graph
    # TODO: vectorise
    for row_index, row in segments.iterrows():
        parent = row['node']
        for item in row['connected_nodes']:
            connected_node = segments.loc[item]['node']
            interaction_graph.add_edge(parent, connected_node)

    # Set transition and filtering rules
    interaction_graph.transition_rules = turn_transition_rules
    interaction_graph.filtering_rules = filter_interactional_sequences

    # Get interactions
    interactional_seqs = interaction_graph.get_chains(
        # kwargs will be used by the transition and filtering rules
        target_participant = target_participant,
        interactants = interactants,
        allow_multi_unit_turns = allow_multi_unit_turns,
        allow_interactions_btw_interactants = allow_interactions_btw_interactants,
        mode = mode,
    )

    # Label interactional sequence and turns
    # print(interactional_seqs)
    flattened_interactional_sequences = list(map(lambda it: sorted([item.index for item in set(flatten(it))]),
                                                 interactional_seqs))
    for index_is, interactional_sequence in enumerate(flattened_interactional_sequences, 1):
        segments.loc[interactional_sequence, 'inter_seq_index'] = index_is
        segments.loc[interactional_sequence, 'conv_turn_index'] = range(1, len(interactional_sequence)+1)

    # Label conversational turns
    segments['inter_seq'] = segments[['inter_seq_index', 'conv_turn_index']].apply(
        lambda row: '({}) '.format(str(row.name)) + '-'.join(
            row.astype(str)if all(map(lambda i:i!='', row.astype(str))) else []),
        axis=1
    )

    segments = segments[['segment_onset', 'segment_offset', 'speaker_type', 'recording_filename',
                         'inter_seq_index', 'conv_turn_index', 'inter_seq']]
    return segments, interactional_seqs


def main(**kwargs):
    interactional_sequences(**kwargs)


if __name__ == '__main__':
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'egs')
    files = os.listdir(root_path)

    segments = []
    for file in files:
        file_segment = pd.read_csv(os.path.join(root_path, file))
        file_segment['recording_filename'] = file
        segments.append(file_segment)

    segments = pd.concat(segments)
    segments = segments[~segments["speaker_type"].isnull()]

    for recording_name, recording_segments in segments.groupby('recording_filename'):
        df_inter_seq, raw_inter_seq = interactional_sequences(
                            segments=recording_segments, target_participant=SPK.CHI,
                            interactants=[SPK.FEM, SPK.MAL], allow_multi_unit_turns=True, allow_segment_jump=True,
                            allow_interactions_btw_interactants=True)
        for index_inter_seq, inter_seq in enumerate(raw_inter_seq):
            print(recording_name)
            InteractionGraph.render(interactional_sequence=inter_seq,
                                    dirpath='/scratch2/whavard/TEMP/graphviz_inter_seq',
                                    name='{}_{}'.format(recording_name, index_inter_seq),
                                    format='png')
        full_path = '~/TEMP/{}.csv'.format(recording_name)
        df_inter_seq.to_csv(full_path, sep='\t', index=False)
        # print(full_path)
        # print(df_inter_seq, len(df_inter_seq))
