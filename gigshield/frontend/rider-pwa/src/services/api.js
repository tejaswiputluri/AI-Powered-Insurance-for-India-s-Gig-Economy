/**
 * GigShield API Service — all backend API calls.
 * Base URL configured via VITE_API_BASE_URL env var.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const IS_DEMO = import.meta.env.VITE_DEMO_MODE === 'true';

console.log('🔧 API Config:', { API_BASE, IS_DEMO });

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('gigshield_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  console.log('📤 API Request:', config.method?.toUpperCase(), config.url, config.data);
  return config;
});

// Response interceptor for consistent error handling
api.interceptors.response.use(
  (response) => {
    console.log('📥 API Response:', response.status, response.data);
    return response.data;
  },
  (error) => {
    console.error('❌ API Error Full Details:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: error.config?.url,
    });
    
    if (!error.response) {
      // Network error - no response from server
      const errMsg = `Network Error: ${error.message || 'Cannot reach API server'}. Trying to reach ${API_BASE}`;
      console.error('🔌 Network Issue:', errMsg);
      const networkError = new Error(errMsg);
      networkError.response = { 
        status: 0,
        data: { 
          detail: { message: errMsg } 
        } 
      };
      throw networkError;
    }
    
    // Re-throw the error with response attached for downstream error handling
    throw error;
  }
);

// ─── Auth ────────────────────────────────────────────────────

export const demoLogin = () => api.post('/auth/demo-login');
export const verifyToken = (firebaseToken) =>
  api.post('/auth/verify-token', { firebase_token: firebaseToken });

// ─── Riders ──────────────────────────────────────────────────

export const onboardRider = (data) => api.post('/riders/onboard', data);
export const getRiderProfile = () => api.get('/riders/me');
export const updateUPI = (upi_vpa) => api.patch('/riders/me/upi', { upi_vpa });

// ─── Policies ────────────────────────────────────────────────

export const createPolicy = (tier) => api.post('/policies/create', { tier });
export const getCurrentPolicy = () => api.get('/policies/me/current');
export const getPolicyHistory = () => api.get('/policies/me/history');
export const simulateCoverage = (params) =>
  api.get('/policies/simulator', { params });

// ─── Claims ──────────────────────────────────────────────────

export const getRiderClaims = () => api.get('/claims/me');
export const getClaimDetail = (claimId) => api.get(`/claims/${claimId}`);
export const getClaimTimeline = (claimId) => api.get(`/claims/${claimId}/timeline`);

// ─── Demo ────────────────────────────────────────────────────

export const demoReset = () => api.post('/demo/reset');
export const demoFireEvent = (scenario) =>
  api.post('/demo/fire-event', { scenario });
export const getDemoState = () => api.get('/demo/state');

// ─── Triggers ────────────────────────────────────────────────

export const getCurrentTriggers = () => api.get('/triggers/current');

export default api;
