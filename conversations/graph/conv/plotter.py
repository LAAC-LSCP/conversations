#!usr/bin/env python
# -*- coding: utf8 -*-

# -----------------------------------------------------------------------------
#   File: plotter.py (as part of project conversations)
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
from typing import List, Set

import graphviz
from itertools import cycle

from conversations.graph.base.Graph import Node
from conversations.utils import pairwise

NODE_START_COLOR = 'chartreuse'
NODE_END_COLOR = 'crimson'
COLOR_LIST = ["lightpink", "lightyellow", "lightskyblue",
              "lightcyan", "lightsteelblue", "lightgrey", "lightslategray", "lightblue",
              "lightgray", "lightgoldenrod", "lightsalmon",
              "lightseagreen", "lightslateblue", "lightgreen", "lightcoral"]


def get_actors(interactional_sequence: List[Node]) -> dict:
    """
    Returns a dictionary of actors with a list of their nodes as value
    :param interactional_sequence: tuple of nodes
    :type interactional_sequence: List[Node]
    :return: dictionary of actors with a list of their nodes as value
    :rtype: dict
    """
    actors = dict()

    for nodes in interactional_sequence:
        for node in nodes:
            actors.setdefault(node.speaker, set())
            actors[node.speaker].add(node)

    for key in actors.keys():
        actors[key] = sorted(actors[key], key=lambda s: s.onset)

    return actors


def _timeline_subgraph(segment_onsets: List[int]) -> graphviz.Digraph:
    """
    Creates a subgraph for the timeline which will be used to nodes
    :param segment_onsets: list of segment onsets
    :type segment_onsets: List[int]
    :return: graphviz Digraph subgraph for the timeline
    :rtype: graphviz.Digraph
    """
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


def _actor_subgraph(actor_names: List[str]) -> graphviz.Digraph:
    """
    Creates a subgraph that contains one anchor node for each actor. This anchor nodes will be connected to the
    first real segment of each actor
    :param actor_names: name of the actor
    :type actor_names: str
    :return: graphviz Digraph subgraph of anchor nodes for each actor and edges between each pair of anchor node
    :rtype: graphviz.Digraph
    """
    # Actor subgraph
    actor_subgraph = graphviz.Digraph(edge_attr={'style': 'invis'},
                                      node_attr={'shape': 'plaintext'},
                                      graph_attr={'rank': 'same'})
    for begin, end in pairwise(sorted(actor_names)):
        actor_subgraph.edge(begin, end)

    return actor_subgraph


def _segment_subgraphs(actors_name_segments: dict, start_nodes: Set[Node], end_nodes: Set[Node]) -> List[graphviz.Digraph]:
    """
    Creates the node for each segment of each actor
    :param actors_name_segments: dictionary of actors with a list of their segments as value
    :type actors_name_segments: dict
    :param start_nodes: list of all the node that are start nodes
    :type start_nodes: Set[Node]
    :param end_nodes: list of all the node that are end nodes
    :type end_nodes: Set[Node]
    :return: list of graphviz Digraph subgraph with one subgraph for each actor, containing all of its nodes
    :rtype: List[graphviz.Digraph]
    """
    graphs = []

    graph_colors = cycle(COLOR_LIST)
    for actor_name, actor_segments in actors_name_segments.items():
        # Subgraph (cluster) declaration (cluster is an obligatory prefix)
        segment_subgraph = graphviz.Digraph(name='cluster_{}'.format(actor_name),
                                            edge_attr={'style': 'invis'},
                                            node_attr={'shape': 'box'},
                                            graph_attr={"bgcolor": next(graph_colors)})
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


def _turn_subgraph(interactional_sequence: List[Node], highlight_edges: List[Node] =[]) -> graphviz.Digraph:
    """
    Creates a subgraph that add the edges that connect the segments together
    :param interactional_sequence: list of edges of the interactional sequence
    :type interactional_sequence: List[Node]
    :param highlight_edges: list of edges that should be hightlighted
    :type highlight_edges: List[Node]
    :return: graphviz Digraph subgraph with edges between segments
    :rtype: graphviz.Digraph
    """
    prompt_response_subgraph = graphviz.Digraph()
    # Add prompt/response edges
    for prompt, response in interactional_sequence:
        color = 'black' if (prompt, response) not in highlight_edges else 'red'
        penwidth = "1" if (prompt, response) not in highlight_edges else "4"
        prompt_response_subgraph.edge(str(prompt), str(response), color=color, penwidth=penwidth)

    return prompt_response_subgraph


def _timeline_alignment_subgraphs(segment_onsets: List, actor_names: List[str]) -> graphviz.Digraph:
    """
    Creates a subgraph that aligns all the segment nodes to their corresponding timeline node
    :param segment_onsets: list of (index, onset) pairs of each node
    :type segment_onsets: list of (index, onset) pairs
    :param actor_names: name of the actors the segments belong to
    :type actor_names: List[str]
    :return: graphviz Digraph subgraph with alignment edges between timeline nodes and segment nodes
    :rtype: graphviz.Digraph
    """
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


def plot(interactional_sequence: List[Node], highlight_edges: List[Node] = []):
    """
    Generates the graph of an interactional sequence
    :param interactional_sequence: tuple of nodes
    :type interactional_sequence: List[Node]
    :param highlight_edges: tuple of nodes whose edges will be highlighted
    :type highlight_edges: List[Node]
    :return: graphviz Digraph object
    :rtype: graphviz.Digraph
    """
    # Sort segments by onset
    sorted_interaction_sequence_turns = sorted(interactional_sequence, key=lambda tup: tup[0].onset)
    prompts, responses = zip(*sorted_interaction_sequence_turns)

    segment_onsets = set([(str(s.index), 'TL{}'.format(s.onset)) for s in prompts+responses])
    segment_onsets = sorted(segment_onsets, key=lambda tup: int(tup[-1].replace('TL', '')))

    actors_name_segments = get_actors(interactional_sequence)

    # Get start and end nodes
    start_nodes = set(prompts) - set(responses)  # all prompts that are not responses
    end_nodes = set(responses) - set(prompts)    # all responses that are not prompts

    # Graph
    graph = graphviz.Digraph(graph_attr={"rankdir": "LR", 'labeljust': 'l', "newrank": "true"})

    actor_subgraph = _actor_subgraph(actors_name_segments.keys())
    timeline_subgraph = _timeline_subgraph(segment_onsets)
    segment_subgraphs = _segment_subgraphs(actors_name_segments, start_nodes, end_nodes)
    timeline_alignment_subgraphs = _timeline_alignment_subgraphs(segment_onsets, actors_name_segments.keys())

    graph.subgraph(actor_subgraph)
    graph.subgraph(timeline_subgraph)
    turn_subgraph = _turn_subgraph(interactional_sequence, highlight_edges=highlight_edges)

    for segment_subgraph in segment_subgraphs:
        graph.subgraph(segment_subgraph)

    for timeline_alignment_subgraph in timeline_alignment_subgraphs:
        graph.subgraph(timeline_alignment_subgraph)

    graph.subgraph(turn_subgraph)

    return graph
