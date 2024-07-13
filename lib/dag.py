# Repository:   https://github.com/Python-utilities
# File Name:    lib/dag.py
# Description:  directed acyclic graph class
#
# Copyright (C) 2024 Dieter J Kybelksties <github@kybelksties.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# @date: 2024-07-13
# @author: Dieter J Kybelksties

import networkx as nx


class DirectedAcyclicGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_edge(self, source, target):
        # Check if adding this edge would create a cycle
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Adding this edge would create a cycle.")

        self.graph.add_edge(source, target)

    def add_node(self, node):
        self.graph.add_node(node)

    def get_in_degree(self, node) -> int:
        return self.graph.in_degree(node)

    def get_out_degree(self, node):
        return self.graph.out_degree(node)

    def depth_first_traversal(self, start_node):
        return list(nx.dfs_preorder_nodes(self.graph, source=start_node))

    def breadth_first_traversal(self, start_node):
        return list(nx.bfs_tree(self.graph, source=start_node))

    def is_acyclic(self):
        return nx.is_directed_acyclic_graph(self.graph)
