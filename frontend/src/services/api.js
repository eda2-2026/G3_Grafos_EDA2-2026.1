import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const client = axios.create({ baseURL: API_BASE_URL });

export const api = {
  async searchArtists(query, limit = 8) {
    const { data } = await client.get('/search', { params: { q: query, limit } });
    return data;
  },

  async getRecommendations(artistName, limit = 10) {
    const { data } = await client.get(`/recommend/${encodeURIComponent(artistName)}`, {
      params: { limit },
    });
    return data;
  },

  async getGraphData(artistId) {
    const { data } = await client.get(`/graph/${encodeURIComponent(artistId)}`);
    return data;
  },
};
