import { useState } from 'react';
import { api } from './services/api';
import SearchBar from './components/SearchBar';
import SeedArtist from './components/SeedArtist';
import RecommendationList from './components/RecommendationList';
import GraphView from './components/GraphView';
import './App.css';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [graphData, setGraphData] = useState(null);

  const handleRecommend = async (artistName, limit) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setGraphData(null);

    try {
      const data = await api.getRecommendations(artistName, limit);
      setResult(data);

      const graph = await api.getGraphData(data.seed_artist.id);
      setGraphData(graph);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'Não foi possível obter recomendações. Verifique se o backend está rodando.',
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="bg-glow" aria-hidden="true" />

      <header className="hero">
        <div className="hero-badge">EDA2 · Grafos · RWR</div>
        <h1>Recomendador Musical</h1>
        <p>
          Descubra artistas similares modelando conexões artista–gênero como um grafo bipartido
          e ranqueando com <em>Random Walk with Restart</em>.
        </p>
      </header>

      <SearchBar onRecommend={handleRecommend} loading={loading} />

      {error && <div className="error-banner" role="alert">{error}</div>}

      {loading && (
        <div className="loading-panel">
          <div className="loader" />
          <p>Montando o grafo e calculando PageRank personalizado...</p>
        </div>
      )}

      {result && !loading && (
        <main className="results-grid">
          <section className="panel">
            <SeedArtist artist={result.seed_artist} />
            <RecommendationList
              recommendations={result.recommendations}
              onSelectArtist={handleRecommend}
            />
          </section>

          <section className="panel graph-panel">
            <h3>Grafo bipartido</h3>
            <GraphView
              graphData={graphData}
              seedId={result.seed_artist.id}
              recommendedIds={result.recommendations.map((r) => r.artist.id)}
            />
          </section>
        </main>
      )}

      <footer>
        <p>Dados via <a href="https://www.last.fm/api" target="_blank" rel="noreferrer">Last.fm API</a></p>
      </footer>
    </div>
  );
}
