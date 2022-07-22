#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: main.py (as part of project conversations)
#   Created: 07/07/2022 14:43
#   Last Modified: 07/07/2022 14:43
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
from glob import glob

from .conversations import Conversation
from .defaults import default_filtering_rules, default_turn_transition_rules, default_path_selection_rules


def main():
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'egs')
    files = [f for f in os.listdir(root_path) if f.endswith('.csv')]

    # Define what a conversation is
    conversation = Conversation(# Participants
                                target_participant='CHI',
                                interactants = ['FEM'],
                                # Connectivity
                                allowed_gap=1000,
                                allow_segment_jump=True,
                                    # Arguments for the user-defined/default_* functions
                                allow_multi_unit_turns=True,
                                allow_interactions_btw_interactants=True,
                                # User-defined rules
                                    # Define how turns are allowed to take place
                                turn_transition_rules=default_turn_transition_rules,
                                    # Select one path amongst several
                                best_path_selection_rules=default_path_selection_rules,
                                    # Filter out interactional sequences
                                filtering_rules=default_filtering_rules,)

    for file in files:
        print(file)

        # Load the data
        data = Conversation.from_csv(os.path.join(root_path, file))
        data = data[~data['speaker_type'].isnull()]  # Remove empty lines

        # Retrieve interactional sequences
        interactional_sequences = conversation.get_interactional_sequences(data)

        # Iterate over all interactional sequences found
        for idx, interactional_sequence in enumerate(interactional_sequences):
            # And plot a graph representing the interactional sequence!
            interactional_sequence.render(dirpath=os.path.join(root_path, 'plots'),
                                          name="{}_{}".format(file, idx),
                                          format='png',
                                          delete_gv=True,
                                          raw_with_best_path=True)
            print('\tPlotted interactional sequence #{}'.format(idx))

        interactional_sequences.to_csv(os.path.join(root_path, 'plots', '{}_interactional_sequences.csv'.format(file)))


if __name__ == '__main__':
    main()
