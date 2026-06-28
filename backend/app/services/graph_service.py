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
