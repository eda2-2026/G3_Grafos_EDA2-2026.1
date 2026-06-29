import { useMemo } from 'react';

function layoutBipartite(nodes, edges, width, height) {
  const artists = nodes.filter((n) => n.type === 'artist');
  const genres = nodes.filter((n) => n.type === 'genre');
  const padding = { top: 40, bottom: 40, left: 120, right: 120 };
  const innerH = height - padding.top - padding.bottom;

  const positions = {};

  artists.forEach((node, i) => {
    const y = padding.top + (innerH / Math.max(artists.length, 1)) * (i + 0.5);
    positions[node.id] = { x: padding.left, y, node };
  });

  genres.forEach((node, i) => {
    const y = padding.top + (innerH / Math.max(genres.length, 1)) * (i + 0.5);
    positions[node.id] = { x: width - padding.right, y, node };
  });

  return { positions, edges };
}

export default function GraphView({ graphData, seedId, recommendedIds = [] }) {
  const width = 720;
  const height = 420;

  const { positions, edges } = useMemo(() => {
    if (!graphData?.nodes?.length) return { positions: {}, edges: [] };
    return layoutBipartite(graphData.nodes, graphData.edges, width, height);
  }, [graphData]);

  if (!graphData?.nodes?.length) {
    return (
      <div className="graph-empty">
        <p>Gere uma recomendação para visualizar o grafo bipartido artista ↔ gênero.</p>
      </div>
    );
  }

  const recSet = new Set(recommendedIds);

  return (
    <div className="graph-container">
      <div className="graph-legend">
        <span><i className="dot seed" /> Semente</span>
        <span><i className="dot rec" /> Recomendado</span>
        <span><i className="dot genre" /> Gênero</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="graph-svg" role="img" aria-label="Grafo bipartido">
        <text x={90} y={24} className="graph-col-label">Artistas</text>
        <text x={width - 90} y={24} className="graph-col-label" textAnchor="end">Gêneros</text>

        {edges.map((edge, i) => {
          const from = positions[edge.source];
          const to = positions[edge.target];
          if (!from || !to) return null;
          return (
            <line
              key={`${edge.source}-${edge.target}-${i}`}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              className="graph-edge"
            />
          );
        })}

        {Object.values(positions).map(({ x, y, node }) => {
          const isGenre = node.type === 'genre';
          const isSeed = node.id === seedId;
          const isRec = recSet.has(node.id);
          const label = node.name?.length > 18 ? `${node.name.slice(0, 16)}…` : node.name;

          if (isGenre) {
            return (
              <g key={node.id} className="graph-node genre-node">
                <rect x={x - 52} y={y - 14} width={104} height={28} rx={14} />
                <text x={x} y={y + 5} textAnchor="middle">{label}</text>
              </g>
            );
          }

          const cls = isSeed ? 'seed-node' : isRec ? 'rec-node' : 'artist-node';
          return (
            <g key={node.id} className={`graph-node ${cls}`}>
              <circle cx={x} cy={y} r={isSeed ? 22 : 18} />
              <text x={x + (isSeed ? 30 : 26)} y={y + 5}>{label}</text>
            </g>
          );
        })}
      </svg>
      <p className="graph-caption">
        {graphData.nodes.filter((n) => n.type === 'artist').length} artistas ·{' '}
        {graphData.nodes.filter((n) => n.type === 'genre').length} gêneros ·{' '}
        {graphData.edges.length} conexões
      </p>
    </div>
  );
}
