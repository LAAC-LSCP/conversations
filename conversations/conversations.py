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
from pprint import pprint

pd.options.display.max_rows = 500
pd.options.display.min_rows = 500

from .Graph import DirectedGraph
from .Interactions import InteractionalSequence, Segment
from .utils import flatten, overlaps
from .defaults import default_turn_transition_rules, default_filtering_rules, default_statistics

class InteractionalSequences(object):
    def __init__(self, data, interactional_sequences, **kwargs):
        self._data = data
        self._interactional_sequences = interactional_sequences

    @property
    def interactional_sequences(self):
        return self._interactional_sequences


    def to_dataframe(self):
        segments = self._data
        # Label interactional sequence and turns
        # print(interactional_seqs)
        flattened_interactional_sequences = list(map(lambda it: sorted([item.index for item in set(flatten(it))]),
                                                     self.interactional_sequences))
        for index_is, interactional_sequence in enumerate(flattened_interactional_sequences, 1):
            segments.loc[interactional_sequence, 'inter_seq_index'] = index_is
            segments.loc[interactional_sequence, 'conv_turn_index'] = range(1, len(interactional_sequence) + 1)

        # Label conversational turns
        segments['inter_seq'] = segments[['inter_seq_index', 'conv_turn_index']].apply(
            lambda row: '({}) '.format(str(row.name)) + '-'.join(
                row.astype(str) if all(map(lambda i: i != '', row.astype(str))) else []),
            axis=1
        )

        return segments


    def __get__(self, index):
        return self._interactional_sequences[index]


    def __iter__(self) -> InteractionalSequence:
        for interacational_sequence in self._interactional_sequences:
            yield interacational_sequence
        return


    def __len__(self):
        return len(self._interactional_sequences)


    def to_csv(self):
        raise NotImplementedError


    def to_chattr(self):
        raise NotImplementedError


class Conversation(object):

    def __init__(self,
                        # target_participant: Union[SPK, str],
                        # interactants:Optional[Union[List[str], List[SPK]]] = None,
                        # Segment connectivity
                        allowed_gap: int = 1000, allowed_overlap:int =0,
                        allow_segment_jump: bool = False,
                        # Filtering
                        min_utt_dur: int = 0, max_utt_dur:int = 0,
                        lx_only:Union[bool, str] = False, lx_col: Union[None, str] = None,
                        # Transitions and filtering rules
                        turn_transition_rules: Optional[Callable] = None,
                        best_path_selection_rules: Optional[Callable] = None,
                        graph_statistics: Optional[Callable] = default_statistics,
                        filtering_rules: Optional[Callable] = None,
                        # Parameters used by the default transition/filtering rules
                        # allow_multi_unit_turns:bool = False,
                        # allow_interactions_btw_interactants: bool = False,
                        **kwargs,
                 ):


        if allowed_overlap: raise NotImplementedError

        # A couple of assertion to make sure everything is right
        assert abs(allowed_gap) == allowed_gap, \
            ValueError('allowed_gap should be positive!')
        assert abs(allowed_overlap) == allowed_overlap, \
            ValueError('allowed_overlap should be positive!')
        assert abs(min_utt_dur) == min_utt_dur, \
            ValueError('min_utt_dur should be positive!')
        assert abs(max_utt_dur) == max_utt_dur, \
            ValueError('max_utt_dur should be positive!')

        if lx_only:
            assert lx_col and type(lx_only) != str, \
                ValueError('Specify which column should be used to assert linguitic type using lx_col parameter.')

        # Speakers
        # self._target_participant = target_participant
        # self._interactants = interactants

        # Segment connectivity
        self._allowed_gap = allowed_gap
        self._allowed_overlap = allowed_overlap
        self._allow_segment_jump = allow_segment_jump

        # Filtering
        self._min_utt_dur = min_utt_dur
        self._max_utt_dur = max_utt_dur
        self._lx_only = lx_only
        self._lx_col = lx_col

        # Transitions rules
        self._turn_transition_rules = turn_transition_rules
        self._filtering_rules = filtering_rules
        self._graph_statistics = graph_statistics
        self._best_path_selection_rules = best_path_selection_rules

        # Parameters used by the default transition
        # self._allow_multi_unit_turns = allow_multi_unit_turns
        # self._allow_interactions_btw_interactants = allow_interactions_btw_interactants

        self._kwargs = kwargs

    #
    #   Properties
    #   (read-only attributes)
    #
    # @property
    # def target_participant(self):
    #     return self._target_participant
    #
    # @property
    # def interactants(self):
    #     return self._interactants
    
    @property
    def allowed_gap(self):
        return self._allowed_gap
    
    @property
    def allowed_overlap(self):
        return self.allowed_overlap
    
    @property
    def allow_segment_jump(self):
        return self._allow_segment_jump
    
    @property
    def min_utt_dur(self):
        return self._min_utt_dur
    
    @property
    def max_utt_dur(self):
        return self._max_utt_dur
    
    @property
    def lx_only(self):
        return self._lx_only
    
    @property
    def lx_col(self):
        return self._lx_col
    
    @property
    def turn_transition_rules(self):
        return self._turn_transition_rules

    @property
    def filtering_rules(self):
        return self._filtering_rules

    @property
    def graph_statistics(self):
        return self._graph_statistics

    @property
    def best_path_selection_rules(self):
        return self._best_path_selection_rules

    # @property
    # def allow_multi_unit_turns(self):
    #     return self._allow_multi_unit_turns
    #
    # @property
    # def allow_interactions_btw_interactants(self):
    #     return self._allow_interactions_btw_interactants
    #
    #
    #   I/O
    #
    @classmethod
    def from_csv(cls, filepath):
        # TODO: add assertion to make sure we have the fields we need
        return pd.read_csv(filepath)


    @classmethod
    def from_rttm(cls, filepath):
        # TODO: should format data so we at least have an
        #  index, a speaker_type, an onset, and an offset
        raise NotImplementedError

    #
    #   Interactional sequences
    #
    def _filter_duration(self, segments):
        # Remove segments based on duration
        segments['segment_duration'] = (segments['segment_offset'] - segments['segment_onset'])
        segments = segments[segments['segment_duration'] > self.min_utt_dur]
        segments = segments[segments['segment_duration'] < self.max_utt_dur] if self.max_utt_dur > 0 else segments

        return segments

    def _filter_lx(self, segments):
        if not self.lx_only:
            return segments

        lx_re = self.lx_only if type(self.lx_only) == str else r'^(?:(?!(J|Y)).)*$' # Remove VCM cries and junk
        segments = segments[segments[self.lx_col].fillna('').str.match(lx_re)]

        return segments

    def _segments_to_nodes(self, segments):
        # Build node for each segment
        # TODO: allow user to store all attributes so that they can use them in the user-defined functions
        segments['node'] = segments.apply(axis=1, func= lambda row: \
                Segment(index=row.name, speaker=row['speaker_type'],
                        onset=row['segment_onset'], offset=row['segment_offset']))

        # For each nodes, get connected nodes
        segments['connected_nodes'] = segments.apply(axis=1,
                func= lambda t_row: segments[
                    segments.apply(axis=1,
                                      # Get overlapping segments
                        func=lambda c_row: (overlaps(c_row['segment_onset'], c_row['segment_offset'],
                                                t_row['segment_onset'], t_row['segment_offset'] + self.allowed_gap))
                                      and c_row['segment_onset'] >= t_row['segment_onset'] # only look after
                                      # Remove identical segments
                                      and t_row.name != c_row.name)
                ])

        if not self.allow_segment_jump:
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

        return segments

    def _segments_to_graph(self, segments):
        interaction_graph = DirectedGraph(transition_rules=self.turn_transition_rules)

        # TODO: vectorise operation?
        for row_index, row in segments.iterrows():
            parent = row['node']
            for item in row['connected_nodes']:
                connected_node = segments.loc[item]['node']
                interaction_graph.add_edge(parent, connected_node)

        return interaction_graph

    def get_interational_sequences(self, data):

        segments = data
        segments.index.name = 'index'

        #   FILTERING
        segments = self._filter_duration(segments)
        segments = self._filter_lx(segments)

        # BUILD LIST OF NODES
        segments = self._segments_to_nodes(segments)
        interaction_graph = self._segments_to_graph(segments)


        connected_components = interaction_graph.get_connected_components(**self._kwargs)

        if self.best_path_selection_rules:
            final_interactional_chains = []
            for connected_component in connected_components:
                pprint(connected_component)
                connected_component_paths = [InteractionalSequence(p, stat_rules=self.graph_statistics)
                                             for p in connected_component.get_all_paths()]
                connected_component_best_path = self.best_path_selection_rules(connected_component_paths)
                final_interactional_chains.append(connected_component_best_path)
        else:
            final_interactional_chains = [InteractionalSequence(p, stat_rules=self.graph_statistics)
                                          for p in connected_components]

        if self.filtering_rules:
            final_interactional_chains = self.filtering_rules(final_interactional_chains, **self._kwargs)

        return InteractionalSequences(data = data, interactional_sequences = final_interactional_chains, **self._kwargs)