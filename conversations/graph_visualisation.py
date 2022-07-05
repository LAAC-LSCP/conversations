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
from .utils import pairwise

def get_actors(interactional_sequence):
    actors = dict()

    for nodes in interactional_sequence:
        for node in nodes:
            actors.setdefault(node.speaker, set())
            actors[node.speaker].add(node)

    for key in actors.keys():
        actors[key] = sorted(actors[key], key=lambda s: s.onset)

    return actors


def generate_interactional_sequence_visualisation(interactional_sequence):
    # Sort segments by onset
    sorted_interaction_sequence_turns = sorted(interactional_sequence, key=lambda tup: tup[0].onset)
    prompts, responses = zip(*sorted_interaction_sequence_turns)

    segment_onsets = set([(str(s.index), 'TL{}'.format(s.onset)) for s in prompts+responses])
    segment_onsets = sorted(segment_onsets, key=lambda tup: tup[-1])

    actors_name_segments = get_actors(interactional_sequence)

    # Get start and end nodes
    start_nodes = set(prompts) - set(responses) # all prompts that are not responses
    end_nodes = set(responses) - set(prompts)   # all responses that are not prompts
    start_color = 'chartreuse'
    end_color = 'crimson'

    # Graph
    graph = graphviz.Digraph(graph_attr={"rankdir":"LR", 'labeljust':'l'})

    # Actor subgraph
    actor_subgraph = graphviz.Digraph(edge_attr={'style': 'invis'}, node_attr={'shape':'plaintext'}, graph_attr={'rank':'same'})
    for actor in actors_name_segments.keys():
        actor_subgraph.node(actor, group='GR{}'.format(actor))
    for begin, end in pairwise(sorted(actors_name_segments.keys())):
        actor_subgraph.edge(begin, end)

    # Timeline subgraph
    tl_subgraph = graphviz.Digraph(edge_attr={'style': 'invis'}, node_attr={'shape': 'box', 'style': 'invis'})
    for _, node in segment_onsets:
        tl_subgraph.node(name=node)
    for (_, begin), (_, end) in pairwise(segment_onsets):
        tl_subgraph.edge(begin, end, style='invis')

    # Segment subgraph
    segment_subgraph = graphviz.Digraph(edge_attr={'style': 'invis'}, node_attr={'shape': 'box'})
    for actor_name, actor_segments in actors_name_segments.items():
        for actor_segment in actor_segments:
            actor_segment_color = 'black'
            actor_segment_color = start_color if actor_segment in start_nodes else actor_segment_color
            actor_segment_color = end_color if actor_segment in end_nodes else actor_segment_color
            node_style = "filled" if actor_segment_color != 'black' else 'solid'
            segment_subgraph.node(str(actor_segment.index), group='GR{}'.format(actor_name),
                                  color=actor_segment_color, style=node_style)
        for begin, end in pairwise(actor_segments):
            segment_subgraph.edge(str(begin.index), str(end.index))

    graph.subgraph(actor_subgraph)
    graph.subgraph(tl_subgraph)
    graph.subgraph(segment_subgraph)

    # Timeline alignment
    for index, onset in segment_onsets:
        tl_segment_subgraph = graphviz.Digraph(graph_attr={'rank': 'same'})
        tl_segment_subgraph.node(index)
        tl_segment_subgraph.node(onset)
        graph.subgraph(tl_segment_subgraph)

    # Add prompt -> response links
    promp_response_subgraph = graphviz.Digraph()
    for prompt, response in interactional_sequence:
        promp_response_subgraph.edge(str(prompt), str(response), label=str((response.onset - prompt.offset)/1000))
    for actor_name, actor_segments in actors_name_segments.items():
        first_segment = actor_segments[0]
        promp_response_subgraph.edge(actor_name, str(first_segment.index), style='invis')

    graph.subgraph(promp_response_subgraph)
    print(graph.source)
