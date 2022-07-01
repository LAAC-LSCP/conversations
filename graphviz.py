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
from itertools import chain

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

    lowest_onset = sorted(chain(*[list(set_) for set_ in actors.values()]), key=lambda node: node.onset)[0]
    highest_offset = sorted(chain(*[list(set_) for set_ in actors.values()]), key=lambda node: node.offset)[-1]

    for actor_label, actor_sequences in actors.items():
        actor_sequences = list(sorted(actor_sequences, key=lambda s:s.index))

        nodes_test = []
        nodes_connections = []
        for idx, (a, b) in enumerate(zip(actor_sequences, actor_sequences[1:]+[None])):
            if a.onset > lowest_onset.onset and idx == 0:
                pre_node_value = '"pre{}" [shape=box, style=invis, width={}];\n'.format(a.index, (a.onset-lowest_onset.onset) / 1000)
                nodes_test.append(pre_node_value)
                nodes_connections.append('"pre{}"'.format(a.index))


            node_value = '"{}" [shape=box, width={}];\n'.format(a.index, (a.offset-a.onset)/1000)
            nodes_test.append(node_value)
            nodes_connections.append('"{}"'.format(a.index))
            # Filling node
            # Todo: add pre-node and post-node to have everything aligned
            if b != None:
                inter_node = '"{}i" [shape=box, width={}, style=invis];\n'.format(a.index, (b.onset - a.offset)/1000)
                nodes_test.append(inter_node)
                nodes_connections.append('"{}i"'.format(a.index))


            if a.offset < highest_offset.offset and idx +1 == len(actor_sequences):
                pre_node_value = '"post{}" [shape=box, style=invis, width={}];\n'.format(a.index, (highest_offset.offset - a.offset) / 1000)
                nodes_test.append(pre_node_value)
                nodes_connections.append('"post{}"'.format(a.index))

            # print(nodes_test)
            # exit()
        print(idx, len(actor_sequences))
        actor_sequences = list(map(str, actor_sequences))
        actor_subgraph = f"""
                subgraph cluster_{actor_label} {{
                node [shape=box, style=filled];
                "{actor_label}_root" [shape=box, style=invis];
                {' '.join(nodes_test)}
                "{actor_label}_root" -> {' -> '.join(nodes_connections)} [style=invis];
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
            actors[node.speaker].add(node)

    return actors

def generate_graphviz(interactional_sequences, recording_name=None):
    for interaction_sequence in interactional_sequences:
        sorted_interaction_sequence_turns = sorted(interaction_sequence, key=lambda tup: tup[0].index)
        prompts, responses = zip(*sorted_interaction_sequence_turns)
        only_responses = set(responses) - set(prompts)

        actors = get_actors(sorted_interaction_sequence_turns)

        actor_subgraphs = build_actors_subgraph(actors)
        sequences_graph = build_sequences_graph(sorted_interaction_sequence_turns)

        beginning_node = '{} [shape=box, color=chartreuse];\n'.format(sorted_interaction_sequence_turns[0][0].index)
        end_nodes = ''
        for end_node in only_responses:
            end_nodes += '{} [shape=box, color=crimson];\n'.format(end_node.index)

        graph_content = actor_subgraphs+sequences_graph+beginning_node+end_nodes
        graph = GRAPH_VIZ_MINIMAL_CODE.format(graph_content)
        if recording_name:
            print(recording_name)
        print(graph)