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
import logging
import re
from operator import attrgetter

from conversations.Graph import DirectedGraph
from conversations.InteractionalSequence import InteractionalSequence
from conversations.PathCost import PathCost
from conversations.Segment import Segment
from conversations.data_importers import from_eaf, from_csv, from_txt, from_rttm, from_its
from conversations.utils import flatten, overlaps

from typing import List, Union, Callable, Optional

import pandas as pd


class InteractionalSequences(object):
    """
    Class used to store all the interactional sequences found for a specific
    """
    def __init__(self, data: pd.DataFrame, interactional_sequences: List[InteractionalSequence]):
        """
        Initiator
        :param data: original data frame containing the segmend
        :type data: pd.DataFrame
        :param interactional_sequences: list of interactional sequences correspond to the input data
        :type interactional_sequences: List[InteractionalSequence]
        """
        self._data = data
        self._interactional_sequences = interactional_sequences

    @property
    def interactional_sequences(self):
        """
        Returns the interactional sequences
        :return: list of interactional sequences
        :rtype: List[InteractionalSequence]
        """
        return self._interactional_sequences

    def to_dataframe(self):
        """
        Save the interactional sequences found for the given input data. Three additional columns are added to the
        original data frame:
            - `inter_seq_index` is the index of the interactional sequence the given segment belongs to
            - 'conv_turn_index' is the index of the segment inside the interactional sequence
            - 'inter_seq' merges the segment index, its inter_seq_index and conv_turn_index into one string
              (which is useful, for example, when loading the data into ELAN)
        :return: dataframe
        :rtype: pd.DataFrame
        """

        def append_column(is_idx, idx, col, payload):
            pad = ','
            if col == 'inter_seq_index' and segments.loc[idx, 'inter_seq_index'] != '':
                if segments.loc[idx, 'inter_seq_index'].split(';')[-1] != str(is_idx):
                    pad = ';'
                else:
                    if col == 'inter_seq_index':
                        return

            if col == 'conv_turn_index' and segments.loc[idx,col] != '':
                if segments.loc[idx, col].split(';')[-1].split(',')[-1] == payload:
                    return

            prev_content = list(filter(lambda t: bool(t) if pad==',' else True, segments.loc[idx, col].split(pad)))
            segments.loc[idx, col] = pad.join(prev_content + [payload])

        segments = self._data.copy()

        # Set up output columns
        segments['unit_index'] = segments.index
        segments['inter_seq_index'] = ''
        segments['conv_turn_index'] = ''
        segments['fmt_inter_seq'] = ''

        # Store whether the node is a start or an end node
        segments['is_start_unit'] = ''
        segments['is_end_unit'] = ''

        # Store to which segment the segment is a prompt/response to
        segments['is_prompt_to'] = ''
        segments['is_response_to'] = ''
        segments['is_self_prompt_to'] = ''
        segments['is_self_response_to'] = ''

        for index_is, interactional_sequence in enumerate(self.interactional_sequences, 1):
            # Concatenate old labelling with new labelling in case interactional chains were disconnected
            indices = sorted(list(set(flatten(interactional_sequence))), key=attrgetter('index'))

            for start_node, end_node in interactional_sequence:
                is_turn_transition = start_node.speaker != end_node.speaker
                is_multi_unit_transition = not(is_turn_transition)

                if is_turn_transition:
                    append_column(index_is, start_node.index, 'is_prompt_to', str(end_node.index))
                    append_column(index_is, end_node.index, 'is_response_to', str(start_node.index))

                if is_multi_unit_transition:
                    append_column(index_is, start_node.index, 'is_self_prompt_to', str(end_node.index))
                    append_column(index_is, end_node.index, 'is_self_response_to', str(start_node.index))


                append_column(index_is, start_node.index, 'inter_seq_index', str(index_is))
                append_column(index_is, start_node.index, 'conv_turn_index', str(indices.index(start_node)+1))
                append_column(index_is, end_node.index, 'inter_seq_index', str(index_is))
                append_column(index_is, end_node.index, 'conv_turn_index', str(indices.index(end_node) + 1))


        segments['is_start_unit'] = segments.apply(axis=1, func=lambda row: (row['is_response_to'] == '' and
                                                                       row['is_self_response_to'] == '')
                                                                       if row['inter_seq_index'] != '' else '')

        segments['is_end_unit'] = segments.apply(axis=1, func=lambda row: (row['is_prompt_to'] == '' and
                                                                     row['is_self_prompt_to'] == '')
                                                                     if row['inter_seq_index'] != '' else '')

        # Label conversational turns
        segments['fmt_inter_seq'] = segments[['inter_seq_index', 'conv_turn_index']].apply(
            lambda row: '({}) '.format(str(row.name)) + ' '.join(
                        map(lambda items: '-'.join(items), zip(filter(bool, row['inter_seq_index'].split(',')),
                                                          filter(bool, row['conv_turn_index'].split(','))))),
            axis=1
        )

        segments = segments.replace('', pd.NA)

        return segments

    def __get__(self, index) -> int:
        """
        Returns the interactional sequence at the given index
        :param index: index
        :type index: int
        :return: interactional sequence
        :rtype: InteractionalSequence
        """
        return self._interactional_sequences[index]

    def __iter__(self) -> Optional[InteractionalSequence]:
        """
        Iterates over the interactional sequence of a file
        :return: interactional sequence
        :rtype: Optional[InteractionalSequence]
        """
        for interactional_sequence in self._interactional_sequences:
            yield interactional_sequence
        return

    def __len__(self) -> int:
        """
        Returns the number of interactional sequence found
        :return: number of interactional sequence
        :rtype: int
        """
        return len(self._interactional_sequences)

    def to_csv(self, filepath) -> None:
        """
        Saves the interactional sequence to a CSV file. For more information on the format used, see `to_dataframe`
        :param filepath: path where the file will be saved
        :type filepath: str
        :return: None
        :rtype: None
        """
        self.to_dataframe().to_csv(filepath, index=False)

    def to_chattr(self):
        raise NotImplementedError


class Conversation(object):
    """
    Class defining the parameters of a conversation
    """
    def __init__(self,  # Only default arguments that specify the names of the columns we are required to have
                        col_segment_speaker,
                        col_segment_onset,
                        col_segment_offset,
                        # Define segment and path cost objects
                        segment_type = Segment,
                        cost_type = PathCost,
                        # Segment connectivity
                        allowed_gap: int = 1000, allowed_overlap: int = 0,
                        allow_segment_jump: bool = False,
                        # Filtering
                        min_utt_dur: int = 0, max_utt_dur: int = 0,
                        lx_only: Union[bool, str] = False, lx_col: Optional[str] = None,
                        # Transitions and filtering rules
                        turn_transition_rules: Optional[Callable] = None,
                        best_path_selection_rules: Optional[Callable] = None,
                        filtering_rules: Optional[Callable] = None,
                        **kwargs, # Used to pass arguments to user-defined functions
                 ):
        """
        Initialisator
        :param segment_type: class that is used to construct represent the segments in the graph. This class should
        be a subclassed from `Node` class
        :type segment_type: Node
        :param cost_type: class that is used to compute the cost of a given path in the graph. This class should
        be a subclassed from `Cost` class
        :type cost_type: Cost
        :param allowed_gap: Maximum amount of time between two segments for them to be considered connected
        :type allowed_gap: int
        :param allowed_overlap: Maximum amount of time two segments are allowed to overlap to be considered connected
        :type allowed_overlap: int
        :param allow_segment_jump: Whether a segment can bind to more than one segment belonging to another
        speaker, if the onset of these segment is within the allowed_gap tolerancy window
        :type allow_segment_jump: bool
        :param min_utt_dur: minimum duration (in milliseconds) a segment should be. All segments that are shorter than
        this value will be removed and won't be considered in the interaction sequence.
        :type min_utt_dur: int
        :param max_utt_dur: maximum duration (in milliseconds) a segment should be. All segments that are longer than
        this value will be removed and won't be considered in the interaction sequence.
        :type max_utt_dur: int
        :param lx_only: Whether only segments that a linguistically valid should be considered. If False, then
        all segments will be considered. Otherwise a regular expression (RegEx) should be used to specify what a
        linguistically valid segment looks like.
        :type lx_only: Union[bool, str]
        :param lx_col: Column used to decide whether a segment is linguistically valid or not
        :type lx_col: Optional[str]
        :param turn_transition_rules: Function that is used to decide whether two segments should be considered linked
        by an edge or not. This allows users to define what a turn is and between whom a turn is allowed to take place.
        :type turn_transition_rules: Optional[Callable]
        :param best_path_selection_rules: Function that is used to score the best path within a raw interactional
        sequence. Users may define they own function. By default, no best path is searched and the raw interactional
        sequence is returned.
        :type best_path_selection_rules: Optional[Callable]
        :param filtering_rules: Function that is used to filter out interactional sequences. Users may define they own
        function. By default, all interactional sequences are returned.
        :type filtering_rules: Optional[Callable]
        :param kwargs: parameters given to the user defined functions (turn_transition_rules, best_path_selection_rules,
        and filtering_rules)
        :type kwargs: dict
        """
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

        self.col_segment_speaker = col_segment_speaker
        self.col_segment_onset = col_segment_onset
        self.col_segment_offset = col_segment_offset

        self.segment_type =  segment_type
        self.cost_type = cost_type

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
        self._best_path_selection_rules = best_path_selection_rules

        self._kwargs = list(kwargs.keys()) # stores arguments to user-defined functions
        # Add them as attributes in case they might be needed
        for _kwargs_key, _kwargs_value in kwargs.items():
            setattr(self, _kwargs_key, _kwargs_value)
    
    @property
    def allowed_gap(self) -> int:
        """
        Returns the attribute _allowed_gap
        :return: maximum allowed gap
        :rtype: int
        """
        return self._allowed_gap
    
    @property
    def allowed_overlap(self) -> int:
        """
        Returns the attribute _allowed_overlap
        :return: maximum allowed overlap
        :rtype: int
        """
        return self._allowed_overlap
    
    @property
    def allow_segment_jump(self) -> bool:
        """
        Returns the attribute _allow_segment_jump
        :return: whether it is allowed to bind to more than one node belonging to the same speaker
        :rtype: bool
        """
        return self._allow_segment_jump
    
    @property
    def min_utt_dur(self) -> int:
        """
        Returns the attribute _min_utt_dur
        :return: minimum allowed duration for a segment
        :rtype: int
        """
        return self._min_utt_dur
    
    @property
    def max_utt_dur(self) -> int:
        """
        Returns the attribute _max_utt_dur
        :return: maximum allowed duration for a segment
        :rtype: int
        """
        return self._max_utt_dur
    
    @property
    def lx_only(self) -> Union[bool, str]:
        """
        Returns the attribute _lx_only
        :return: the RegEx used to assess linguistic validity or False
        :rtype: Union[bool, str]
        """
        return self._lx_only
    
    @property
    def lx_col(self) -> str:
        """
        Returns the attribute _lx_col
        :return: the name of the column use to assess linguistic validity
        :rtype: str
        """
        return self._lx_col
    
    @property
    def turn_transition_rules(self) -> Callable:
        """
        Returns the attribute _turn_transition_rules
        :return: user-defined turn transition rules
        :rtype: Callable
        """
        return self._turn_transition_rules

    @property
    def filtering_rules(self) -> Callable:
        """
        Returns the attribute _filtering_rules
        :return: user-defined filtering function
        :rtype: Callable
        """
        return self._filtering_rules

    @property
    def best_path_selection_rules(self) -> Callable:
        """
        Returns the attribute _best_path_selection_rules
        :return: user-defined best path selection function
        :rtype: Callable
        """
        return self._best_path_selection_rules

    @property
    def user_defined_arguments(self):
        return {kwargs_key: getattr(self, kwargs_key) for kwargs_key in self._kwargs}

    #
    #   I/O
    #
    @classmethod
    def from_csv(cls, filepath) -> pd.DataFrame:
        """
        Reads a CSV file and return a data frame
        :param filepath: path to the CSV file to be read
        :type filepath: str
        :return: pandas DataFrame
        :rtype: pd.DataFrame
        """
        return from_csv(filepath)

    @classmethod
    def from_rttm(cls, filepath, name_mapping=None, source_file:str = None):
        """
        Reads a RTTM file and return a data frame with columns {"segment_onset","segment_offset","speaker_type"}
        :param filepath: path to the RTTM file to be read
        :type filepath: str
        :param name_mapping: mapping of the names used in the RTTM to new names, defaults to None, keeping the original names
        :type name_mapping: dict
        :param source_file: only keep lines belonging to that file, when not set, every line will be kept even if from different recordings
        :type source_file: str
        :return: pandas DataFrame
        :rtype: pd.DataFrame
        """
        return from_rttm(filepath, name_mapping, source_file)
    
    @classmethod
    def from_its(cls, filepath, speaker_mapping = None, recording_num = None) -> pd.DataFrame:
        """
        Reads an ITS file and return a data frame with columns {"segment_onset","segment_offset","speaker_type"}
        :param filepath: path to the ITS file to be read
        :type filepath: str
        :param recording_num: only keep lines belonging to that recording number, when not set, every line will be kept even if from different recordings
        :type recording_num: int
        :return: pandas DataFrame
        :rtype: pd.DataFrame
        """
        return from_its(filepath, speaker_mapping, recording_num)
    
    @classmethod
    def from_txt(cls, filepath) -> pd.DataFrame:
        """
        Reads a txt file and return a data frame. The input .txt should be a plain-text,
        tab-separated file with a header row that contains the column names.
        The three columns must be speaker_type , segment_onset , segment_offset
        :param filepath: path to the txt file to be read
        :type filepath: str
        :return: pandas DataFrame
        :rtype: pd.DataFrame
        """
        return from_txt(filepath)
    
    @classmethod
    def from_eaf(cls, filepath) -> pd.DataFrame:
        """
        Reads a EAF file and return a data frame. All the existing tiers are imported
        and the name of the tier is used as the value for speaker_type
        :param filepath: path to the CSV file to be read
        :type filepath: str
        :return: pandas DataFrame
        :rtype: pd.DataFrame
        """
        return from_eaf(filepath)
    
    
    #
    #   Interactional sequences
    #
    def _filter_duration(self, segments) -> pd.DataFrame:
        """
        Filters out segment based on their durations
        :param segments: data frame containing segments
        :type segments: pd.DataFrame
        :return: input data frame with segments that are too long or too short removed
        :rtype: pd.DataFrame
        """
        # Remove segments based on duration
        segments['segment_duration'] = (segments['segment_offset'] - segments['segment_onset'])
        segments = segments[segments['segment_duration'] > self.min_utt_dur]
        segments = segments[segments['segment_duration'] < self.max_utt_dur] if self.max_utt_dur > 0 else segments

        return segments

    def _filter_lx(self, segments) -> pd.DataFrame:
        """
        Filters out segment based on their linguistic validity
        :param segments: data frame containing segments
        :type segments: pd.DataFrame
        :return: input data frame with segments that not linguistically valid removed
        :rtype: pd.DataFrame
        """
        if not self.lx_only:
            return segments

        lx_re = self.lx_only if type(self.lx_only) == str else r'^(?:(?!(J|Y)).)*$'  # Remove VCM cries and junk
        segments = segments[segments[self.lx_col].fillna('').str.match(lx_re)]

        return segments

    def _segments_to_nodes(self, segments) -> pd.DataFrame:
        """
        Convert each input segment to a Segment object
        :param segments: data frame containing segments
        :type segments: pd.DataFrame
        :return: input data frame with original columns and one additional column
        :rtype: pd.DataFrame
        """
        # Build node for each segment
        segments['node'] = segments.apply(axis=1, func=lambda row:
                self.segment_type(index=row.name, speaker=row['speaker_type'],
                                  onset=row['segment_onset'], offset=row['segment_offset'], **row))
        return segments

    def _find_connected_nodes(self, segments) -> pd.DataFrame:
        """
        For each node, find connected nodes and add the index of these nodes to the column `connected_nodes`
        :param segments: data frame containing segments
        :type segments: pd.DataFrame
        :return: input data frame with original columns and one additional column containing the index of the
        nodes connected to it
        :rtype: pd.DataFrame
        """

        # For each nodes, get connected nodes
        segments['connected_nodes'] = segments.apply(axis=1,
                func=lambda t_row: segments[
                    segments.apply(axis=1,
                                      # Get overlapping segments
                        func=lambda c_row: (overlaps(c_row['segment_onset'], c_row['segment_offset'],
                                                t_row['segment_onset'], t_row['segment_offset'] + self.allowed_gap))
                                      # only look after. /!\ only use > and not >= as it might create cycles
                                      and c_row['segment_onset'] > t_row['segment_onset']
                                      # Remove identical segments
                                      and t_row.name != c_row.name)
                ])

        if not self.allow_segment_jump:
            # Timeline  | t = t0 <-------------------------------------> t = t0 + allowed_gap
            # Target    |            |----------|
            # Candidate |               |---Keep---| |--Remove--|
            segments['connected_nodes'] = segments['connected_nodes'].apply(
                func=lambda df: (df.groupby('speaker_type')
                                # Keep only the first segment for each candidate speaker
                                .apply(lambda rows: (rows.sort_values(by='segment_onset', ascending=True)
                                                    .head(n=1)))
                                # Remove multi-indexing and keep original index
                                .apply(lambda rows: rows if not rows.index.nlevels > 1
                                                    else rows.droplevel(0))))

        # Retrieve indexes of connected nodes
        segments['connected_nodes'] = segments['connected_nodes'].apply(lambda df: list(df.index))
        return segments

    def _segments_to_graph(self, segments) -> DirectedGraph:
        """
        Create a graph from the nodes and their connections
        :param segments: data frame containing the segments
        :type segments: pd.DataFrame
        :return: a directed graph whose edges reflect the connexion between nodes
        :rtype: DirectedGraph
        """
        interaction_graph = DirectedGraph(transition_rules=self.turn_transition_rules)

        nodes = segments[['node', 'connected_nodes']]
        for row_index, row in nodes.iterrows():
            parent = row['node']
            for item in row['connected_nodes']:
                connected_node = nodes.loc[item]['node']
                interaction_graph.add_edge(parent, connected_node)
        return interaction_graph

    def get_interactional_sequences(self, data) -> InteractionalSequences:
        """
        Finds interactional sequences for the input data given the current conversational settings
        :param data: data frame of segments
        :type data: pd.DataFrame
        :return: InteractionalSequences object containing interactional sequences found in the input data
        :rtype: InteractionalSequences
        """

        # Get data and set index name
        segments = data
        segments.index.name = 'index'

        # Filter out segments
        segments = self._filter_duration(segments)
        segments = self._filter_lx(segments)

        # Build list of nodes and build graph
        segments = self._segments_to_nodes(segments)
        segments = self._find_connected_nodes(segments)
        interaction_graph = self._segments_to_graph(segments)

        # Find interactional sequences
        connected_components = interaction_graph.get_connected_components(**self.user_defined_arguments)

        # Transform connected components edges to graph
        interactional_sequences = [InteractionalSequence(p) for p in connected_components]

        # Find best path for each connected component (if necessary)
        if self.best_path_selection_rules:
            for inter_seq in interactional_sequences:
                best_path = inter_seq._interactional_sequence.best_path(self.cost_type,
                                                                        self.best_path_selection_rules,
                                                                        **self.user_defined_arguments)
                inter_seq._best_path = DirectedGraph.from_tuple_list(best_path)
        # Filter out sequences
        if self.filtering_rules:
            interactional_sequences = self.filtering_rules(interactional_sequences, **self.user_defined_arguments)

        return InteractionalSequences(data=data, interactional_sequences=interactional_sequences)
