/**
 * Dashboard — active coverage home screen.
 * Shows: status banner, zone risk, active disruption, recent claims, quick actions.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getRiderProfile, getCurrentPolicy, getRiderClaims, demoFireEvent, getDemoState } from '../services/api';
import { formatRupees, getStatusDisplay, formatIST } from '../utils/formatters';
import toast from 'react-hot-toast';

const IS_DEMO = import.meta.env.VITE_DEMO_MODE !== 'false';

export default function Dashboard() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [policy, setPolicy] = useState(null);
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [firingEvent, setFiringEvent] = useState(false);

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  async function loadDashboard() {
    try {
      const [demoState] = await Promise.all([getDemoState()]);
      const state = demoState?.data;

      if (state) {
        setProfile(state.rider);
        setPolicy(state.policy);
        setClaims(state.claims || []);
      }
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleFireEvent(scenario) {
    setFiringEvent(true);
    try {
      const res = await demoFireEvent(scenario);
      toast.success(`⚡ ${res.scenario_description}`);
      setTimeout(loadDashboard, 1000);
    } catch (err) {
      toast.error(err.response?.data?.detail?.message || 'Failed to fire event');
    } finally {
      setFiringEvent(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-navy-500 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4 animate-pulse">⚡</div>
          <p className="text-white/50">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const isCovered = policy?.status === 'active';
  const hasActiveClaim = claims.some(c => ['pending_fraud_check', 'fraud_checking', 'approved'].includes(c.status));

  return (
    <div className="min-h-screen bg-navy-500 pb-24">
      {/* Header */}
      <div className="px-6 pt-6 pb-4 flex items-center justify-between">
        <div>
          <p className="text-white/40 text-sm">Welcome back</p>
          <h1 className="text-xl font-bold">{profile?.name || 'Rider'}</h1>
        </div>
        <span className="text-2xl">⚡</span>
      </div>

      {/* Status Banner */}
      <motion.div
        className={`mx-6 mb-4 p-4 rounded-xl ${
          isCovered
            ? 'bg-green-500/10 border border-green-500/30'
            : 'bg-red-500/10 border border-red-500/30'
        }`}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{isCovered ? '🟢' : '🔴'}</span>
          <div>
            <p className="font-bold text-lg">{isCovered ? 'COVERED THIS WEEK' : 'NOT COVERED'}</p>
            {isCovered && policy && (
              <p className="text-white/50 text-sm">
                {formatRupees(policy.weekly_premium_paise || 6700)} deducted Monday · Coverage active
              </p>
            )}
          </div>
        </div>
      </motion.div>

      {/* Zone Risk Card */}
      <motion.div
        className="mx-6 mb-4 glass-card p-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <p className="text-white/40 text-xs uppercase tracking-wider mb-2">Your Zone This Week</p>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-lg font-bold">{profile?.zone_id?.replace(/_/g, ' ') || 'BTM Layout'}</p>
            <p className="text-white/50 text-sm">Zone risk level</p>
          </div>
          <span className="px-3 py-1 rounded-full text-sm font-bold bg-orange-500/20 text-orange-400">
            HIGH
          </span>
        </div>
      </motion.div>

      {/* Active Disruption */}
      {hasActiveClaim && (
        <motion.div
          className="mx-6 mb-4 glass-card p-4 border border-gold-500/30 disruption-pulse"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">⚡</span>
            <p className="font-bold text-gold-500">Disruption Detected!</p>
          </div>
          {claims.filter(c => c.status !== 'rejected').slice(0, 1).map(claim => (
            <div key={claim.id} className="flex justify-between items-center">
              <div>
                <p className="text-sm text-white/60">
                  Claim processing · Score: {claim.confidence_score}/100
                </p>
              </div>
              <p className="text-xl font-bold gold-gradient">
                {formatRupees(claim.payout_paise)}
              </p>
            </div>
          ))}
        </motion.div>
      )}

      {/* Recent Claims */}
      <div className="mx-6 mb-4">
        <div className="flex items-center justify-between mb-3">
          <p className="text-white/40 text-xs uppercase tracking-wider">Recent Claims</p>
          <button
            onClick={() => navigate('/claims')}
            className="text-gold-500 text-xs font-medium"
          >
            View All →
          </button>
        </div>

        {claims.length === 0 ? (
          <div className="glass-card p-6 text-center">
            <p className="text-white/30">No claims yet</p>
            <p className="text-white/20 text-sm mt-1">Claims are created automatically when disruption is detected</p>
          </div>
        ) : (
          <div className="space-y-2">
            {claims.slice(0, 3).map((claim) => {
              const status = getStatusDisplay(claim.status);
              return (
                <motion.button
                  key={claim.id}
                  onClick={() => navigate(`/claim/${claim.id}`)}
                  className="w-full glass-card p-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
                  whileTap={{ scale: 0.98 }}
                >
                  <div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${status.bg} ${status.color}`}>
                      {status.label}
                    </span>
                    <p className="text-white/50 text-xs mt-1">
                      Score: {claim.confidence_score}/100
                    </p>
                  </div>
                  <p className="text-lg font-bold">
                    {formatRupees(claim.payout_paise)}
                  </p>
                </motion.button>
              );
            })}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="mx-6 mb-4 grid grid-cols-2 gap-3">
        <button
          onClick={() => navigate('/simulator')}
          className="glass-card p-4 text-center hover:bg-white/5 transition-colors"
        >
          <span className="text-2xl block mb-1">📊</span>
          <span className="text-sm text-white/60">Simulate Payout</span>
        </button>
        <button
          onClick={() => navigate('/claims')}
          className="glass-card p-4 text-center hover:bg-white/5 transition-colors"
        >
          <span className="text-2xl block mb-1">📋</span>
          <span className="text-sm text-white/60">Claim History</span>
        </button>
      </div>

      {/* Demo Controls */}
      {IS_DEMO && (
        <div className="mx-6 mt-6">
          <p className="text-white/20 text-xs uppercase tracking-wider mb-3">Demo Controls</p>
          <div className="grid grid-cols-2 gap-2">
            {[
              { scenario: 'rain_aqi', label: '🌧 Rain + Orders', color: 'from-blue-600 to-blue-800' },
              { scenario: 'full_3_signal', label: '⚡ Full 3-Signal', color: 'from-gold-600 to-gold-800' },
              { scenario: 'aqi_order', label: '😷 AQI + Orders', color: 'from-orange-600 to-orange-800' },
              { scenario: 'fraud_attempt', label: '🚨 Fraud Test', color: 'from-red-600 to-red-800' },
            ].map(({ scenario, label, color }) => (
              <button
                key={scenario}
                onClick={() => handleFireEvent(scenario)}
                disabled={firingEvent}
                className={`bg-gradient-to-r ${color} p-3 rounded-xl text-sm font-medium disabled:opacity-50 hover:opacity-90 transition-opacity`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
