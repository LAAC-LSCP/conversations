#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: example.py (as part of project conversations)
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

from conversations import Conversation
from conversations.defaults import standard_filtering_rules, standard_turn_transition_rules, standard_path_selection_rules


def main():
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    plot_path = os.path.join(root_path, 'plots')
    csv_path = os.path.join(root_path, 'csv')

    os.makedirs(plot_path, exist_ok=True)
    os.makedirs(csv_path, exist_ok=True)

    files = [f for f in os.listdir(root_path) if f.endswith('.csv')]

    # Define what a conversation is
    conversation = Conversation(# Participants
                                target_participant='CHI',
                                # Connectivity
                                allowed_gap=1000,
                                allow_segment_jump=False,
                                    # Arguments for the user-defined/default_* functions
                                allow_multi_unit_turns=True,
                                allow_interactions_btw_interactants=True,
                                selection_key=['num_turns', 'num_multi_turns_transitions'],
                                # User-defined rules
                                    # Define how turns are allowed to take place
                                turn_transition_rules=standard_turn_transition_rules,
                                    # Select one path amongst several
                                best_path_selection_rules=standard_path_selection_rules,
                                    # Filter out interactional sequences
                                filtering_rules=standard_filtering_rules,)

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
            interactional_sequence.render(dirpath=plot_path,
                                          name="{}_{}".format(file, idx),
                                          format='png',
                                          delete_gv=False,
                                          raw_with_best_path=False)
            print('\tPlotted interactional sequence #{}'.format(idx))

        output_fn = '{}_interactional_sequences.csv'.format(os.path.splitext(file)[0])
        interactional_sequences.to_csv(os.path.join(csv_path, output_fn))


if __name__ == '__main__':
    main()
