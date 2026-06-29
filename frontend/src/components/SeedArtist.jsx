function formatListeners(n) {
  if (n == null) return null;
  return `${n.toLocaleString('pt-BR')} ouvintes`;
}

export default function SeedArtist({ artist }) {
  return (
    <div className="seed-card">
      <div className="seed-visual">
        {artist.image_url ? (
          <img src={artist.image_url} alt={artist.name} />
        ) : (
          <div className="avatar-placeholder large">♪</div>
        )}
      </div>
      <div className="seed-info">
        <span className="seed-label">Artista de partida</span>
        <h2>{artist.name}</h2>
        {artist.popularity != null && (
          <p className="listeners">{formatListeners(artist.popularity)}</p>
        )}
        {artist.genres?.length > 0 && (
          <div className="tags">
            {artist.genres.map((g) => (
              <span key={g} className="tag">{g}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
