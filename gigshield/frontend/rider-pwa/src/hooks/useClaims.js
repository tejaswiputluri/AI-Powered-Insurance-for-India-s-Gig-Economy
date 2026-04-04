/**
 * useClaims Hook — Claims polling, detail, and timeline management.
 * Polls for new claims every 30 seconds when a policy is active.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { getRiderClaims, getClaimDetail, getClaimTimeline } from '../services/api';

const POLL_INTERVAL_MS = 30000; // 30 seconds

export function useClaims({ autoPolling = true } = {}) {
  const [claims, setClaims] = useState([]);
  const [totalClaims, setTotalClaims] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  const fetchClaims = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getRiderClaims();
      setClaims(response?.data?.claims || []);
      setTotalClaims(response?.data?.total || 0);
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Failed to fetch claims');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchClaimDetail = useCallback(async (claimId) => {
    try {
      const response = await getClaimDetail(claimId);
      return response?.data || null;
    } catch (err) {
      console.error('Failed to fetch claim detail:', err);
      return null;
    }
  }, []);

  const fetchClaimTimeline = useCallback(async (claimId) => {
    try {
      const response = await getClaimTimeline(claimId);
      return response?.events || [];
    } catch (err) {
      console.error('Failed to fetch claim timeline:', err);
      return [];
    }
  }, []);

  // Auto-polling
  useEffect(() => {
    fetchClaims(); // Initial fetch

    if (autoPolling) {
      pollRef.current = setInterval(fetchClaims, POLL_INTERVAL_MS);
    }

    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
      }
    };
  }, [fetchClaims, autoPolling]);

  return {
    claims,
    totalClaims,
    loading,
    error,
    fetchClaims,
    fetchClaimDetail,
    fetchClaimTimeline,
  };
}
