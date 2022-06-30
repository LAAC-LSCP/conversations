#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: graphviz.py (as part of project conversations)
#   Created: 29/06/2022 17:11
#   Last Modified: 29/06/2022 17:11
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

from pprint import pprint

GRAPH_VIZ_MINIMAL_CODE = """
digraph G {{
	fontname="Helvetica,Arial,sans-serif"
	node [fontname="Helvetica,Arial,sans-serif"]
	edge [fontname="Helvetica,Arial,sans-serif"]
	rankdir="LR";
	labeljust="l";
    
    {}
}}
"""

def build_actors_subgraph(actors):
    # Declare actors invisible nodes
    actors_invisible_node = '\n'.join([f'"{actor}" [style = invis];' for actor in actors.keys()])
    actors_ordering = ' -> '.join(sorted(actors.keys()))
    actors_invisible_nodes = f"""
    {{ 
	    rank=same;
        {actors_invisible_node}
        {actors_ordering} [style=invis];
    }}
    """

    # Add nodes to each actor
    actors_subgraph = ''
    for actor_label, actor_sequences in actors.items():
        actor_sequences = list(sorted(actor_sequences))
        actor_sequences = list(map(str, actor_sequences))
        actor_subgraph = f"""
                subgraph cluster_{actor_label} {{
                node [style=filled];
                "{actor_label}_root" [style=invis];
                "{actor_label}_root" -> {' -> '.join(actor_sequences)} [style=invis];
                label = "{actor_label}";
            }}
        """
        actors_subgraph += actor_subgraph

    # Link invisible ordering nodes to actors root nodes
    ordering_nodes_to_root_nodes = ''
    for actor_label in actors.keys():
        ordering_nodes_to_root_nodes += f'"{actor_label}" -> "{actor_label}_root" [style=invis];\n'

    actors_graphs = actors_invisible_nodes + actors_subgraph + ordering_nodes_to_root_nodes
    return actors_graphs

def build_sequences_graph(interactional_sequence):
    turn_graph = ''
    for candidate, connected in interactional_sequence:
        if candidate.speaker != connected.speaker:
            turn_graph += '{} -> {} [constraint=true];\n'.format(candidate.index, connected.index)
        else:
            turn_graph += '{} -> {} [constraint=true, color=blue];\n'.format(candidate.index, connected.index)
    return turn_graph

def get_actors(interactional_sequence):
    actors = dict()
    for nodes in interactional_sequence:
        for node in nodes:
            actors.setdefault(node.speaker, set())
            actors[node.speaker].add(node.index)

    return actors

def generate_graphviz(interactional_sequences):
    for interaction_sequence in interactional_sequences:
        sorted_interaction_sequence_turns = sorted(interaction_sequence, key=lambda tup: tup[0].index)
        prompts, responses = zip(*sorted_interaction_sequence_turns)
        only_responses = set(responses) - set(prompts)

        actors = get_actors(sorted_interaction_sequence_turns)

        actor_subgraphs = build_actors_subgraph(actors)
        sequences_graph = build_sequences_graph(sorted_interaction_sequence_turns)

        beginning_node = '{} [shape=doublecircle, color=chartreuse];\n'.format(sorted_interaction_sequence_turns[0][0].index)
        end_nodes = ''
        for end_node in only_responses:
            end_nodes += '{} [shape=doublecircle, color=crimson];\n'.format(end_node.index)

        graph_content = actor_subgraphs+sequences_graph+beginning_node+end_nodes
        graph = GRAPH_VIZ_MINIMAL_CODE.format(graph_content)
        print(graph)