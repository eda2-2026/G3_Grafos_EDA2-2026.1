from typing import Optional

import networkx as nx

GENRE_PREFIX = "genre::"


class GraphService:

    def __init__(self) -> None:
        """Inicializa um grafo vazio e não-direcionado."""
        self.graph: nx.Graph = nx.Graph()

    @staticmethod
    def genre_node(genre: str) -> str:
        return f"{GENRE_PREFIX}{genre.strip().lower()}"

    @staticmethod
    def is_artist_node(node: str) -> bool:
        return not str(node).startswith(GENRE_PREFIX)

    def add_artist_genre_edges(
        self, artist_id: str, artist_name: str, genres: list[str]
    ) -> None:
        self.graph.add_node(artist_id, type="artist", name=artist_name)

        for genre in genres or []:
            if not isinstance(genre, str) or not genre.strip():
                continue
            g_node = self.genre_node(genre)
            self.graph.add_node(g_node, type="genre", name=genre.strip().lower())
            self.graph.add_edge(artist_id, g_node, weight=1.0)

    def has_artist(self, artist_id: str) -> bool:
        return (
            self.graph.has_node(artist_id)
            and self.graph.nodes[artist_id].get("type") == "artist"
        )

    def get_graph_data(self, artist_id: Optional[str] = None) -> dict:
        # Exporta {"nodes":[{id,type,name}], "edges":[{source,target,weight}]}.
        # Com artist_id, restringe ao componente conexo (ou vazio se ausente).
        graph = self.graph
        if artist_id is not None:
            if artist_id not in graph:
                return {"nodes": [], "edges": []}
            graph = graph.subgraph(nx.node_connected_component(graph, artist_id))

        nodes = [
            {"id": node, "type": data.get("type"), "name": data.get("name", node)}
            for node, data in graph.nodes(data=True)
        ]
        edges = [
            {"source": u, "target": v, "weight": data.get("weight", 1.0)}
            for u, v, data in graph.edges(data=True)
        ]
        return {"nodes": nodes, "edges": edges}
