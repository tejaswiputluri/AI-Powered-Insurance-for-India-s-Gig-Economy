/**
 * Fraud Queue — pending claims requiring insurer review.
 * Shows all 4 fraud layer scores with approve/reject actions.
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getFraudQueue, fraudDecision } from '../services/api';

function formatRupees(paise) {
  return `₹${Math.round((paise || 0) / 100).toLocaleString('en-IN')}`;
}

function ScoreBadge({ score, maxScore, result }) {
  const pct = maxScore > 0 ? (score / maxScore) * 100 : 0;
  const color = result === 'pass' ? 'text-green-400' : result === 'fail' ? 'text-red-400' : 'text-gray-400';
  return (
    <span className={`font-bold ${color}`}>{score}/{maxScore}</span>
  );
}

export default function FraudQueue() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deciding, setDeciding] = useState({});

  useEffect(() => {
    loadQueue();
    const interval = setInterval(loadQueue, 15000);
    return () => clearInterval(interval);
  }, []);

  async function loadQueue() {
    try {
      const res = await getFraudQueue();
      setQueue(res.data || []);
    } catch (err) {
      console.error('Failed to load fraud queue:', err);
    }
    setLoading(false);
  }

  async function handleDecision(claimId, decision) {
    setDeciding({ ...deciding, [claimId]: true });
    try {
      await fraudDecision(claimId, decision);
      await loadQueue();
    } catch (err) {
      console.error('Decision failed:', err);
    }
    setDeciding({ ...deciding, [claimId]: false });
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Fraud Review Queue</h1>
          <p className="text-white/40 text-sm">
            Claims requiring manual review · {queue.length} pending
          </p>
        </div>
        <button
          onClick={loadQueue}
          className="px-4 py-2 bg-white/5 rounded-lg text-sm hover:bg-white/10 transition-colors"
        >
          ↻ Refresh
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-white/50">Loading...</div>
      ) : queue.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <span className="text-4xl block mb-4">✅</span>
          <p className="text-white/50 text-lg">Queue is clear!</p>
          <p className="text-white/30 text-sm mt-2">No claims pending review</p>
        </div>
      ) : (
        <div className="space-y-4">
          <AnimatePresence>
            {queue.map((item, i) => (
              <motion.div
                key={item.claim_id}
                className="glass-card p-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="font-bold text-lg">{item.rider_name}</p>
                    <p className="text-white/40 text-sm">{item.zone_id?.replace(/_/g, ' ')} · {item.time_waiting_minutes} min waiting</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-[#E89B0A]">{formatRupees(item.claim_amount_paise)}</p>
                    <p className="text-white/40 text-sm">Score: {item.confidence_score}/100</p>
                  </div>
                </div>

                {/* 4-Layer Scores */}
                <div className="grid grid-cols-4 gap-3 mb-4">
                  <div className="bg-white/5 rounded-lg p-3">
                    <p className="text-xs text-white/40 mb-1">L1: GPS</p>
                    <ScoreBadge score={item.l1_gps_score} maxScore={30} result={item.l1_gps_result} />
                  </div>
                  <div className="bg-white/5 rounded-lg p-3">
                    <p className="text-xs text-white/40 mb-1">L2: Weather</p>
                    <ScoreBadge score={item.l2_weather_score} maxScore={30} result={item.l2_weather_result} />
                  </div>
                  <div className="bg-white/5 rounded-lg p-3">
                    <p className="text-xs text-white/40 mb-1">L3: Earnings</p>
                    <ScoreBadge score={item.l3_earnings_score} maxScore={25} result={item.l3_earnings_result} />
                  </div>
                  <div className="bg-white/5 rounded-lg p-3">
                    <p className="text-xs text-white/40 mb-1">L4: Cluster</p>
                    <ScoreBadge score={item.l4_cluster_score} maxScore={15} result={item.l4_cluster_result} />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={() => handleDecision(item.claim_id, 'approve')}
                    disabled={deciding[item.claim_id]}
                    className="flex-1 bg-green-500/20 text-green-400 py-3 rounded-lg font-medium hover:bg-green-500/30 transition-colors disabled:opacity-50"
                  >
                    ✓ Approve Payout
                  </button>
                  <button
                    onClick={() => handleDecision(item.claim_id, 'reject')}
                    disabled={deciding[item.claim_id]}
                    className="flex-1 bg-red-500/20 text-red-400 py-3 rounded-lg font-medium hover:bg-red-500/30 transition-colors disabled:opacity-50"
                  >
                    ✗ Reject
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
