import { useEffect, useRef, useState } from 'react';
import { api } from '../services/api';

export default function SearchBar({ onRecommend, loading }) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searching, setSearching] = useState(false);
  const [limit, setLimit] = useState(10);
  const wrapperRef = useRef(null);

  useEffect(() => {
    if (query.trim().length < 2) {
      setSuggestions([]);
      return undefined;
    }

    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const data = await api.searchArtists(query, 6);
        setSuggestions(data.results || []);
        setShowSuggestions(true);
      } catch {
        setSuggestions([]);
      } finally {
        setSearching(false);
      }
    }, 350);

    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const submit = (artistName) => {
    const name = (artistName || query).trim();
    if (!name) return;
    setQuery(name);
    setShowSuggestions(false);
    onRecommend(name, limit);
  };

  return (
    <div className="search-section" ref={wrapperRef}>
      <form
        className="search-form"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <div className="search-input-wrap">
          <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            placeholder="Ex: Radiohead, Beyoncé, Caetano Veloso..."
            disabled={loading}
            autoComplete="off"
          />
          {searching && <span className="input-spinner" />}
        </div>

        <select
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          disabled={loading}
          aria-label="Quantidade de recomendações"
        >
          {[5, 10, 15, 20].map((n) => (
            <option key={n} value={n}>{n} resultados</option>
          ))}
        </select>

        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Analisando...' : 'Recomendar'}
        </button>
      </form>

      {showSuggestions && suggestions.length > 0 && (
        <ul className="suggestions">
          {suggestions.map((artist) => (
            <li key={artist.id}>
              <button type="button" onClick={() => submit(artist.name)}>
                {artist.image_url ? (
                  <img src={artist.image_url} alt="" />
                ) : (
                  <span className="avatar-placeholder">♪</span>
                )}
                <span className="suggestion-info">
                  <strong>{artist.name}</strong>
                  {artist.popularity != null && (
                    <small>{artist.popularity.toLocaleString('pt-BR')} ouvintes</small>
                  )}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
