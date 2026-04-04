/**
 * GigShield Insurer Dashboard API Service.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Insurer auth — demo mode bypasses
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('gigshield_insurer_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
);

export const getOverview = () => api.get('/insurer/overview');
export const getHeatmap = () => api.get('/insurer/heatmap');
export const getFraudQueue = () => api.get('/insurer/fraud-queue');
export const fraudDecision = (claimId, decision, note = '') =>
  api.post(`/insurer/fraud-queue/${claimId}/decision`, { decision, note });
export const getAllClaims = (params) => api.get('/insurer/claims', { params });
export const getReserves = () => api.get('/insurer/reserves');

// Triggers
export const getCurrentTriggers = () => api.get('/triggers/current');
export const getTriggerHistory = (zoneId = 'BTM_LAYOUT', days = 7) =>
  api.get('/triggers/history', { params: { zone_id: zoneId, days } });

export default api;
