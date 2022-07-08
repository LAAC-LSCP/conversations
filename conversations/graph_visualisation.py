#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: graph_visualisation.py (as part of project conversations)
#   Created: 05/07/2022 13:46
#   Last Modified: 05/07/2022 13:46
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

import graphviz
from itertools import cycle

from .utils import pairwise

NODE_START_COLOR = 'chartreuse'
NODE_END_COLOR = 'crimson'
COLOR_LIST = ["lightpink","lightyellow","lightskyblue",
              "lightgoldenrodyellow","lightcyan","lightsteelblue",
              "lightgrey","lightslategray","lightblue",
              "lightgray","lightgoldenrod","lightsalmon",
              "lightseagreen","lightslateblue","lightgreen","lightcoral"]

def get_actors(interactional_sequence):
    actors = dict()

    for nodes in interactional_sequence:
        for node in nodes:
            actors.setdefault(node.speaker, set())
            actors[node.speaker].add(node)

    for key in actors.keys():
        actors[key] = sorted(actors[key], key=lambda s: s.onset)

    return actors

def _timeline_subgraph(segment_onsets):
    tl_subgraph = graphviz.Digraph(edge_attr={'style': 'invis'},
                                   node_attr={'shape': 'box', 'style': 'invis'})
    # Normal nodes
    for _, node in segment_onsets:
        tl_subgraph.node(name=node)
    for (_, begin), (_, end) in pairwise(segment_onsets):
        tl_subgraph.edge(begin, end, style='invis')
    # End node
    tl_subgraph.node(name="TLEND")
    tl_subgraph.edge(end, "TLEND", style='invis')
    
    return tl_subgraph

def _actor_subgraph(actor_names):
    # Actor subgraph
    actor_subgraph = graphviz.Digraph(edge_attr={'style': 'invis'},
                                      node_attr={'shape':'plaintext'},
                                      graph_attr={'rank':'same'})
    for begin, end in pairwise(sorted(actor_names)):
        actor_subgraph.edge(begin, end)

    return actor_subgraph

def _segment_subgraphs(actors_name_segments, start_nodes, end_nodes):
    graphs = []

    graph_colors = cycle(COLOR_LIST)
    for actor_name, actor_segments in actors_name_segments.items():
        # Subgraph (cluster) declaration (cluster is an obligatory prefix)
        segment_subgraph = graphviz.Digraph(name='cluster_{}'.format(actor_name),
                                            edge_attr={'style': 'invis'},
                                            node_attr={'shape': 'box'},
                                            graph_attr={"bgcolor":next(graph_colors)})
        # Add begin node and end node
        segment_subgraph.node(actor_name, group='GR{}'.format(actor_name), shape="plaintext")
        segment_subgraph.node('{}END'.format(actor_name), group='GR{}'.format(actor_name), style='invis')

        # Add segment nodes
        for actor_segment in actor_segments:
            actor_segment_color = 'black'
            actor_segment_color = NODE_START_COLOR if actor_segment in start_nodes else actor_segment_color
            actor_segment_color = NODE_END_COLOR if actor_segment in end_nodes else actor_segment_color
            node_style = "filled" if actor_segment_color != 'black' else 'solid'
            segment_subgraph.node(str(actor_segment.index), group='GR{}'.format(actor_name),
                                  color=actor_segment_color, style=node_style)

        # Add links between nodes
        for begin, end in pairwise(actor_segments):
            segment_subgraph.edge(str(begin.index), str(end.index), constraint="false")

        # Link last node to end node and first node to start node
        segment_subgraph.edge(actor_name, str(actor_segments[0].index))
        segment_subgraph.edge(str(actor_segments[-1].index), '{}END'.format(actor_name))

        # Add to graph pool
        graphs.append(segment_subgraph)

    return graphs

def _turn_subgraph(interactional_sequence, label_edges=False):
    prompt_response_subgraph = graphviz.Digraph()
    # Add prompt/response edges
    for prompt, response in interactional_sequence:
        label = str((response.onset - prompt.offset)/1000) if label_edges else ''
        prompt_response_subgraph.edge(str(prompt), str(response), label=label)

    return prompt_response_subgraph

def _timeline_alignment_subgraphs(segment_onsets, actor_names):
    graphs = []

    # Align each speaker's node to the right timeline node
    for index, onset in segment_onsets:
        tl_segment_subgraph = graphviz.Digraph(graph_attr={'rank': 'same'})
        tl_segment_subgraph.node(index)
        tl_segment_subgraph.node(onset)
        graphs.append(tl_segment_subgraph)

    # Align END_ and TLEND
    tl_segment_subgraph = graphviz.Digraph(graph_attr={'rank': 'same'})
    tl_segment_subgraph.node("TLEND")
    for actor_name in actor_names:
        tl_segment_subgraph.node('{}END'.format(actor_name))
    graphs.append(tl_segment_subgraph)

    return graphs

def generate_interactional_sequence_visualisation(interactional_sequence, label_edges=False):
    # Sort segments by onset
    sorted_interaction_sequence_turns = sorted(interactional_sequence, key=lambda tup: tup[0].onset)
    prompts, responses = zip(*sorted_interaction_sequence_turns)

    segment_onsets = set([(str(s.index), 'TL{}'.format(s.onset)) for s in prompts+responses])
    segment_onsets = sorted(segment_onsets, key=lambda tup: int(tup[-1].replace('TL', '')))

    actors_name_segments = get_actors(interactional_sequence)

    # Get start and end nodes
    start_nodes = set(prompts) - set(responses) # all prompts that are not responses
    end_nodes = set(responses) - set(prompts)   # all responses that are not prompts

    # Graph
    graph = graphviz.Digraph(graph_attr={"rankdir":"LR", 'labeljust':'l', "newrank":"true"})

    actor_subgraph = _actor_subgraph(actors_name_segments.keys())
    timeline_subgraph = _timeline_subgraph(segment_onsets)
    segment_subgraphs = _segment_subgraphs(actors_name_segments, start_nodes, end_nodes)
    timeline_alignment_subgraphs = _timeline_alignment_subgraphs(segment_onsets, actors_name_segments.keys())

    graph.subgraph(actor_subgraph)
    graph.subgraph(timeline_subgraph)
    turn_subgraph = _turn_subgraph(interactional_sequence, label_edges=label_edges)

    for segment_subgraph in segment_subgraphs:
        graph.subgraph(segment_subgraph)

    for timeline_alignment_subgraph in timeline_alignment_subgraphs:
        graph.subgraph(timeline_alignment_subgraph)

    graph.subgraph(turn_subgraph)

    return graph
