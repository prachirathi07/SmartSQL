import axios from 'axios';
import { QueryResponse, DatabaseSchema } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  health: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  getSchema: async (): Promise<DatabaseSchema> => {
    const response = await api.get('/api/schema');
    return response.data;
  },

  processQuery: async (query: string): Promise<QueryResponse> => {
    const response = await api.post('/api/query', { query });
    return response.data;
  },
}; 