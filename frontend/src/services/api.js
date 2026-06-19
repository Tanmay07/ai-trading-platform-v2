import axios from 'axios';

const API_BASE = 'http://localhost:8000';



const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getMarketSummary = async () => {
  const response = await api.get('/portfolio');
  return response.data;
};

export const addPortfolioHolding = async (data) => {
  const response = await api.post('/portfolio', data);
  return response.data;
};

export const updatePortfolioHolding = async (symbol, data) => {
  const response = await api.put(`/portfolio/${symbol}`, data);
  return response.data;
};

export const deletePortfolioHolding = async (symbol) => {
  const response = await api.delete(`/portfolio/${symbol}`);
  return response.data;
};

export const getMarketHistory = async (symbol) => {
  const response = await api.get(`/market/history/${symbol}?period=1y`);
  return response.data;
};

export const getSentiment = async (symbol) => {
  const response = await api.get(`/sentiment/${symbol}?days=7`);
  return response.data;
};

export const getPrediction = async (symbol) => {
  const response = await api.get(`/predictions/${symbol}`);
  return response.data;
};

export const runBacktest = async (data) => {
  const response = await api.post('/backtest/run', data);
  return response.data;
};

export const getBacktestRuns = async () => {
  const response = await api.get('/backtest/runs');
  return response.data;
};

export const getBacktestRunById = async (id) => {
  const response = await api.get(`/backtest/runs/${id}`);
  return response.data;
};

export const getSectors = async () => {
  const response = await api.get('/market/sectors');
  return response.data;
};

export const refreshSectors = async () => {
  const response = await api.post('/market/sectors/refresh');
  return response.data;
};

export const trainBatch = async (symbols, period = '3y', n_iter = 10) => {
  const response = await api.post('/ml/train_batch', { symbols, period, n_iter });
  return response.data;
};

export const getStrategy = async (symbols) => {
  const response = await api.post('/predictions/strategy', { symbols });
  return response.data;
};

export const getTargetProfitSuggestions = async (target = 5000, maxCapital = null) => {
  const params = new URLSearchParams();
  params.append('target', target);
  if (maxCapital) params.append('max_capital', maxCapital);
  
  const response = await api.get(`/suggestions/target-profit?${params.toString()}`);
  return response.data;
};

export default api;
