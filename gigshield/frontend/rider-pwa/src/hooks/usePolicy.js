/**
 * usePolicy Hook — Policy CRUD operations and state management.
 * Manages current policy, policy history, and tier selection.
 */

import { useState, useEffect, useCallback } from 'react';
import { getCurrentPolicy, createPolicy, getPolicyHistory } from '../services/api';

export function usePolicy() {
  const [currentPolicy, setCurrentPolicy] = useState(null);
  const [policyHistory, setPolicyHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCurrentPolicy = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getCurrentPolicy();
      setCurrentPolicy(response?.data || null);
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Failed to fetch policy');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPolicyHistory = useCallback(async () => {
    try {
      const response = await getPolicyHistory();
      setPolicyHistory(response?.data || []);
    } catch (err) {
      console.error('Failed to fetch policy history:', err);
    }
  }, []);

  const activatePolicy = useCallback(async (tier) => {
    setLoading(true);
    setError(null);
    try {
      const response = await createPolicy(tier);
      await fetchCurrentPolicy();  // Refresh
      return response;
    } catch (err) {
      const message = err.response?.data?.detail?.message || 'Failed to create policy';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchCurrentPolicy]);

  // Auto-fetch on mount
  useEffect(() => {
    fetchCurrentPolicy();
    fetchPolicyHistory();
  }, [fetchCurrentPolicy, fetchPolicyHistory]);

  return {
    currentPolicy,
    policyHistory,
    loading,
    error,
    fetchCurrentPolicy,
    fetchPolicyHistory,
    activatePolicy,
  };
}
