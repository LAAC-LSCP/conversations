#!usr/bin/env python
# -*- coding: utf8 -*-
#
# -----------------------------------------------------------------------------
#   File: toolbox.py (as part of project conversations)
#   Created: 07/09/2022 12:38
#   Last Modified: 07/09/2022 12:38
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
from typing import List

import pandas as pd


def count_num_turn_transitions(df: pd.DataFrame, speakers: List, speaker_column:str) -> int:
    """
    Return the number of turn transitions between two speakers
    :param df: DataFrame of conversational interactions
    :type df: pd.DataFrame
    :param speakers:
    :type speakers: List
    :return: number of turn transitions
    :rtype: int
    """
    return len(get_turn_transitions_between_pair(df, speakers, speaker_column))


def get_turn_transitions_between_pair(df: pd.DataFrame, speakers: List, speaker_column:str) -> pd.DataFrame:
    """
    Returns a DataFrame of turn transitions between two speakers.
    Each row should be interpreted as a turn transition between the segment `is_response_to` (corresponding to the index
    of the segment that constitutes the prompt) and the segment `unit_index`.
    /!\ This only works when a best path was found !
    :param df: DataFrame of conversational interactions
    :type df: pd.DataFrame
    :param speakers:
    :type speakers: List
    :return: DataFrame of segments where each row corresponds to a turn transition between the two desired speakers.
    :rtype: pd.DataFrame
    """
    assert len(speakers) == 2, ValueError('`speakers` should only contain two speakers!')
    assert speaker_column in df.columns, ValueError('Speaker column `{}` not found!'.format(speaker_column))

    # Only keep speakers in the speaker list, and who have segments belonging to an interactional sequence
    segs = df[df[speaker_column].isin(speakers) &
              ~df['inter_seq_index'].isnull()]

     # In case of multiple values in is_prompt_to and is_response_to, explode the lines to be considered separated
    segs['is_response_to'] = segs['is_response_to'].astype('string').str.split(',')
    segs = segs.explode('is_response_to')
    segs.loc[~segs['is_response_to'].isnull(),'is_response_to'] = segs[~segs['is_response_to'].isnull()]['is_response_to'].astype(float)

    segs['is_prompt_to'] = segs['is_prompt_to'].astype('string').str.split(',')
    segs = segs.explode('is_prompt_to')
    segs.loc[~segs['is_prompt_to'].isnull(),'is_prompt_to'] = segs[~segs['is_prompt_to'].isnull()]['is_prompt_to'].astype(float)
    
    # Convert strings to pandas Int32 (/!\ not np.int32)
    segs = segs.astype({'is_response_to': 'Int32', 'is_prompt_to': 'Int32'})

    # Get all prompts and responses
    all_prompt_responses = list(segs[segs['is_response_to'].notnull()]['is_response_to']) + \
                           list(segs[segs['is_prompt_to'].notnull()]['is_prompt_to'])

    # Keep segments that are prompts are responses, and that are in the df
    turns = segs[segs['unit_index'].isin(all_prompt_responses) &
                 segs['is_response_to'].isin(segs['unit_index']) &
                 segs['is_response_to'].notnull()]

    return turns