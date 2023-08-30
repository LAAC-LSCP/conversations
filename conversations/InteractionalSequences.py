#!usr/bin/env python
# -*- coding: utf8 -*-
#
# -----------------------------------------------------------------------------
#   File: InteractionalSequences.py (as part of project conversations)
#   Created: 21/03/2023 14:08
#   Last Modified: 21/03/2023 14:08
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
from typing import List, Optional

import pandas as pd

from conversations.InteractionalSequence import InteractionalSequence


class InteractionalSequences(object):
    """
    Class used to store all the interactional sequences found for a specific
    """
    def __init__(self, data: pd.DataFrame, interactional_sequences: List[InteractionalSequence]):
        """
        Initiator
        :param data: original data frame containing the segments
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
