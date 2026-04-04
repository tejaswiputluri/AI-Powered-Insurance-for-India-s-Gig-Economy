/**
 * useAuth Hook — Manages authentication state and demo login flow.
 * DEMO_MODE: Auto-login with demo credentials.
 * PROD_MODE: Firebase phone OTP → backend JWT exchange.
 */

import { useState, useEffect, useCallback } from 'react';
import { demoLogin, verifyToken } from '../services/api';

const TOKEN_KEY = 'gigshield_token';
const RIDER_KEY = 'gigshield_rider_id';

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [riderId, setRiderId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check existing token on mount
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    const savedRiderId = localStorage.getItem(RIDER_KEY);
    if (token && savedRiderId) {
      setIsAuthenticated(true);
      setRiderId(savedRiderId);
    }
    setLoading(false);
  }, []);

  const loginDemo = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await demoLogin();
      const { rider_id, access_token } = response;
      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(RIDER_KEY, rider_id);
      setIsAuthenticated(true);
      setRiderId(rider_id);
      return true;
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Demo login failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const loginFirebase = useCallback(async (firebaseToken) => {
    setLoading(true);
    setError(null);
    try {
      const response = await verifyToken(firebaseToken);
      const { rider_id, is_new_rider, access_token } = response;
      if (access_token) {
        localStorage.setItem(TOKEN_KEY, access_token);
        localStorage.setItem(RIDER_KEY, rider_id);
        setIsAuthenticated(true);
        setRiderId(rider_id);
      }
      return { riderId: rider_id, isNewRider: is_new_rider };
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Firebase login failed');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(RIDER_KEY);
    setIsAuthenticated(false);
    setRiderId(null);
  }, []);

  return {
    isAuthenticated,
    riderId,
    loading,
    error,
    loginDemo,
    loginFirebase,
    logout,
  };
}
