export default function RecommendationList({ recommendations, onSelectArtist }) {
  if (!recommendations?.length) {
    return (
      <div className="empty-state">
        <p>Nenhuma recomendação encontrada para este artista.</p>
      </div>
    );
  }

  const maxScore = recommendations[0]?.score || 1;

  return (
    <div className="recommendations">
      <h3>Recomendações via Random Walk with Restart</h3>
      <ol className="rec-list">
        {recommendations.map((rec, index) => (
          <li key={rec.artist.id} className="rec-item">
            <span className="rank">#{index + 1}</span>
            <button
              type="button"
              className="rec-main"
              onClick={() => onSelectArtist?.(rec.artist.name)}
              title={`Explorar ${rec.artist.name}`}
            >
              {rec.artist.image_url ? (
                <img src={rec.artist.image_url} alt="" />
              ) : (
                <span className="avatar-placeholder">♪</span>
              )}
              <span className="rec-info">
                <strong>{rec.artist.name}</strong>
                {rec.artist.genres?.length > 0 && (
                  <small>{rec.artist.genres.slice(0, 3).join(' · ')}</small>
                )}
              </span>
            </button>
            <div className="score-bar-wrap">
              <div
                className="score-bar"
                style={{ width: `${(rec.score / maxScore) * 100}%` }}
              />
              <span className="score">{(rec.score * 100).toFixed(1)}%</span>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
