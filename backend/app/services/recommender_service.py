import networkx as nx

from app.services.graph_service import GraphService
DEFAULT_ALPHA: float = 0.85


class RecommenderService:

    def __init__(
        self, graph_service: GraphService, alpha: float = DEFAULT_ALPHA
    ) -> None:
        self.graph_service = graph_service
        self.alpha = alpha

    def get_recommendations(
        self, artist_id: str, top_n: int = 10
    ) -> list[tuple[str, float]]:
        graph = self.graph_service.graph
        if graph.number_of_nodes() == 0 or artist_id not in graph:
            return []
        if graph.degree(artist_id) == 0:
            return []
        component = nx.node_connected_component(graph, artist_id)
        subgraph = graph.subgraph(component)

        try:
            scores = nx.pagerank(
                subgraph,
                alpha=self.alpha,
                personalization={artist_id: 1.0},
                weight="weight",
            )
        except nx.PowerIterationFailedConvergence:
            return []

        recommendations = [
            (node, score)
            for node, score in scores.items()
            if node != artist_id and self.graph_service.is_artist_node(node)
        ]

        recommendations.sort(key=lambda item: (-item[1], item[0]))
        return recommendations[:top_n]
