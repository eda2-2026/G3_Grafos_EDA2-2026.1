import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  async searchArtist(query) {
    const response = await axios.get(`${API_BASE_URL}/search`, { params: { q: query } });
    return response.data;
  },
  
  async getRecommendations(artistName, limit = 10) {
    const response = await axios.get(`${API_BASE_URL}/recommend/${encodeURIComponent(artistName)}`, {
      params: { limit }
    });
    return response.data;
  },
  
  async getGraphData(artistId) {
    const response = await axios.get(`${API_BASE_URL}/graph/${artistId}`);
    return response.data;
  }
};