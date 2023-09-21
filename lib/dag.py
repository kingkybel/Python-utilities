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
