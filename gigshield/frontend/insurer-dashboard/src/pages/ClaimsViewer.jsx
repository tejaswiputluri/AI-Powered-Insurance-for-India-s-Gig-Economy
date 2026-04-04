/**
 * Claims Viewer — paginated list of all claims with filters.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getAllClaims } from '../services/api';

function formatRupees(paise) {
  return `₹${Math.round((paise || 0) / 100).toLocaleString('en-IN')}`;
}

const statusColors = {
  approved: 'text-green-400 bg-green-500/20',
  paid: 'text-green-400 bg-green-500/20',
  auto_approved: 'text-green-400 bg-green-500/20',
  flagged: 'text-yellow-400 bg-yellow-500/20',
  on_hold: 'text-orange-400 bg-orange-500/20',
  rejected: 'text-red-400 bg-red-500/20',
};

export default function ClaimsViewer() {
  const [claims, setClaims] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadClaims();
  }, [statusFilter]);

  async function loadClaims() {
    setLoading(true);
    try {
      const res = await getAllClaims({ status: statusFilter, limit: 50 });
      setClaims(res.data || []);
    } catch (err) {
      setClaims([]);
    }
    setLoading(false);
  }

  const filters = ['all', 'approved', 'flagged', 'on_hold', 'rejected', 'paid'];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">All Claims</h1>
      <p className="text-white/40 text-sm mb-6">Complete claims registry</p>

      {/* Filters */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {filters.map(f => (
          <button
            key={f}
            onClick={() => setStatusFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm capitalize transition-colors ${
              statusFilter === f
                ? 'bg-[#E89B0A]/20 text-[#E89B0A] font-semibold'
                : 'bg-white/5 text-white/50 hover:bg-white/10'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Claims Table */}
      {loading ? (
        <div className="text-center py-12 text-white/50">Loading...</div>
      ) : claims.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <p className="text-white/50">No claims found</p>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/5">
                <th className="px-4 py-3 text-left text-xs text-white/40 font-medium">Rider</th>
                <th className="px-4 py-3 text-left text-xs text-white/40 font-medium">Zone</th>
                <th className="px-4 py-3 text-right text-xs text-white/40 font-medium">Payout</th>
                <th className="px-4 py-3 text-center text-xs text-white/40 font-medium">Score</th>
                <th className="px-4 py-3 text-center text-xs text-white/40 font-medium">Status</th>
                <th className="px-4 py-3 text-right text-xs text-white/40 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {claims.map((claim, i) => {
                const colors = statusColors[claim.status] || 'text-gray-400 bg-gray-500/20';
                return (
                  <motion.tr
                    key={claim.id}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.03 }}
                  >
                    <td className="px-4 py-3 text-sm">{claim.rider_name || 'Unknown'}</td>
                    <td className="px-4 py-3 text-sm text-white/60">{claim.zone_id?.replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3 text-sm text-right font-medium">
                      {formatRupees(claim.capped_payout_paise)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`text-sm font-bold ${
                        (claim.confidence_score || 0) >= 85 ? 'text-green-400' :
                        (claim.confidence_score || 0) >= 60 ? 'text-yellow-400' :
                        (claim.confidence_score || 0) >= 35 ? 'text-orange-400' : 'text-red-400'
                      }`}>
                        {claim.confidence_score || '-'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full ${colors} capitalize`}>
                        {claim.fraud_decision || claim.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-white/40 text-right">
                      {new Date(claim.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
