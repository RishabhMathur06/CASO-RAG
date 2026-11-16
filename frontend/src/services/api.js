import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60s timeout for local LLM inference
});

export const checkHealth = async () => {
  try {
    const res = await apiClient.get('/health');
    return res.data;
  } catch (error) {
    return { status: 'offline', error: error.message };
  }
};

export const queryRAG = async (query, topK = 3) => {
  const startTime = performance.now();
  const res = await apiClient.post('/rag/query', { query, top_k: topK });
  const clientLatencyMs = (performance.now() - startTime).toFixed(1);

  return {
    ...res.data,
    clientLatencyMs,
    serverProcessTimeMs: res.headers['x-process-time-ms'] || null,
  };
};

export const ingestDocument = async (title, text) => {
  const res = await apiClient.post('/rag/ingest', { title, text });
  return res.data;
};

export const clearRedisCache = async () => {
  const res = await apiClient.delete('/rag/cache');
  return res.data;
};