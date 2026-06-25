import React, { useState } from 'react';
import { api } from './services/api';
import './App.css';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await api.getRecommendations(searchTerm);
      setRecommendations(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao buscar recomendações');
      setRecommendations(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>🎵 Recomendador Musical</h1>
        <p>Digite um artista e descubra novos sons!</p>
      </header>
      
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Ex: Radiohead, Beyoncé, Caetano Veloso..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Buscando...' : 'Recomendar'}
        </button>
      </form>
      
      {error && <div className="error">{error}</div>}
      
      {recommendations && (
        <div className="results">
          <div className="seed-artist">
            <h2>🎯 {recommendations.seed_artist.name}</h2>
            <p>Gêneros: {recommendations.seed_artist.genres.join(', ')}</p>
          </div>
          
          <div className="recommendations">
            <h3>Recomendações:</h3>
            <ul>
              {recommendations.recommendations.map((rec, index) => (
                <li key={rec.artist.id}>
                  <span className="rank">#{index + 1}</span>
                  <span className="name">{rec.artist.name}</span>
                  <span className="score">{(rec.score * 100).toFixed(2)}%</span>
                  <span className="genres">{rec.artist.genres.join(', ')}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;