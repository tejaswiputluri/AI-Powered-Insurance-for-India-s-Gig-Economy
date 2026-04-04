/**
 * ClaimHistory — full list of all past claims with timeline.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getRiderClaims } from '../services/api';
import { formatRupees, getStatusDisplay, formatIST } from '../utils/formatters';

export default function ClaimHistory() {
  const navigate = useNavigate();
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadClaims();
  }, []);

  async function loadClaims() {
    try {
      const res = await getRiderClaims();
      setClaims(res?.data?.claims || []);
    } catch (err) {
      console.error('Failed to load claims:', err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-navy-500 px-6 py-8">
      <button onClick={() => navigate(-1)} className="text-white/40 text-sm mb-4 hover:text-white/60">
        ← Back
      </button>
      <h1 className="text-2xl font-bold mb-6">Claim History</h1>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-white/50">Loading claims...</p>
        </div>
      ) : claims.length === 0 ? (
        <div className="glass-card p-8 text-center">
          <span className="text-4xl block mb-4">📋</span>
          <p className="text-white/50">No claims yet</p>
          <p className="text-white/30 text-sm mt-2">
            Claims are auto-created when disruption is detected in your zone
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {claims.map((claim, i) => {
            const status = getStatusDisplay(claim.status);
            return (
              <motion.button
                key={claim.id}
                onClick={() => navigate(`/claim/${claim.id}`)}
                className="w-full glass-card p-4 text-left hover:bg-white/5 transition-colors"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${status.bg} ${status.color}`}>
                    {status.label}
                  </span>
                  <span className="text-white/30 text-xs">
                    {formatIST(claim.created_at)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-white/50">
                      Score: {claim.confidence_score}/100
                    </p>
                  </div>
                  <p className="text-xl font-bold gold-gradient">
                    {formatRupees(claim.capped_payout_paise)}
                  </p>
                </div>
              </motion.button>
            );
          })}
        </div>
      )}
    </div>
  );
}
