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

from .conversations import Conversation
from .defaults import default_filtering_rules, default_turn_transition_rules, \
                      default_path_selection_rules, default_statistics


def main():
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'egs')
    files = os.listdir(root_path)

    # Define what a conversation is
    conversation = Conversation(# Participants
                                target_participant='CHI',
                                # Connectivity
                                allowed_gap=1000,
                                allow_segment_jump=True,
                                    # Arguments for the user defined functions
                                allow_multi_unit_turns=True,
                                allow_interactions_btw_interactants=True,
                                # User-defined rules
                                    # Define how turns are allowed to take place
                                turn_transition_rules=default_turn_transition_rules,
                                    # Select one path amongst several
                                best_path_selection_rules=default_path_selection_rules,
                                graph_statistics=default_statistics,
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
            # Print some descriptive information
            print(interactional_sequence)
            # And plot a graph representing the interactional sequence!
            interactional_sequence.render(dirpath="/scratch2/whavard/TEMP",
                                          name="{}_{}".format(file, idx),
                                          format='png')

        interactional_sequences.to_csv('/scratch2/whavard/TEMP/{}_interactional_sequences.csv'.format(file))


if __name__ == '__main__':
    main()
