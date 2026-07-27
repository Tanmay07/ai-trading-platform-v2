import api from './api';

export const getPortfolios = async () => {
  const response = await api.get('/api/v2/portfolio');
  return response.data;
};

export const createPortfolio = async (data) => {
  const response = await api.post('/api/v2/portfolio', data);
  return response.data;
};

export const getPortfolioHoldings = async (id) => {
  const response = await api.get(`/api/v2/portfolio/${id}/holdings`);
  return response.data;
};

export const getPortfolioSummary = async (id) => {
  const response = await api.get(`/api/v2/portfolio/${id}/summary`);
  return response.data;
};

export const addTransaction = async (id, data) => {
  const response = await api.post(`/api/v2/portfolio/${id}/transaction`, data);
  return response.data;
};
