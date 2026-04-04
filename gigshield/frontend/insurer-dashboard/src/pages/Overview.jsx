/**
 * Overview — KPI cards with this week's metrics.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getOverview } from '../services/api';

function formatRupees(paise) {
  return `₹${Math.round((paise || 0) / 100).toLocaleString('en-IN')}`;
}

export default function Overview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const res = await getOverview();
      setData(res.this_week);
    } catch (err) {
      // Use mock data for demo
      setData({
        active_riders: 847,
        premium_collected_paise: 5674900,
        claims_paid_paise: 2890400,
        loss_ratio: 0.509,
        claims_auto_approved: 23,
        claims_flagged: 4,
        claims_rejected: 2,
      });
    }
    setLoading(false);
  }

  if (loading) return <div className="text-white/50">Loading...</div>;

  const kpis = [
    {
      label: 'Active Riders',
      value: data?.active_riders?.toLocaleString() || '0',
      icon: '🏍️',
      color: 'from-blue-500/10 to-blue-600/5',
      border: 'border-blue-500/20',
    },
    {
      label: 'Premium Collected',
      value: formatRupees(data?.premium_collected_paise),
      icon: '💰',
      color: 'from-green-500/10 to-green-600/5',
      border: 'border-green-500/20',
    },
    {
      label: 'Claims Paid',
      value: formatRupees(data?.claims_paid_paise),
      icon: '📤',
      color: 'from-orange-500/10 to-orange-600/5',
      border: 'border-orange-500/20',
    },
    {
      label: 'Loss Ratio',
      value: `${((data?.loss_ratio || 0) * 100).toFixed(1)}%`,
      icon: '📉',
      color: data?.loss_ratio > 0.70
        ? 'from-red-500/10 to-red-600/5'
        : 'from-emerald-500/10 to-emerald-600/5',
      border: data?.loss_ratio > 0.70 ? 'border-red-500/20' : 'border-emerald-500/20',
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Dashboard Overview</h1>
      <p className="text-white/40 text-sm mb-8">This week's performance</p>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {kpis.map((kpi, i) => (
          <motion.div
            key={kpi.label}
            className={`bg-gradient-to-br ${kpi.color} ${kpi.border} border rounded-2xl p-6`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <span className="text-2xl">{kpi.icon}</span>
            <p className="text-white/50 text-sm mt-3">{kpi.label}</p>
            <p className="text-2xl font-bold mt-1">{kpi.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Fraud Decision Breakdown */}
      <div className="grid grid-cols-3 gap-4">
        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-sm text-white/50">Auto-Approved</p>
          <p className="text-3xl font-bold text-green-400 mt-2">
            {data?.claims_auto_approved || 0}
          </p>
          <p className="text-xs text-white/30 mt-1">Confidence ≥ 85</p>
        </motion.div>

        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <p className="text-sm text-white/50">Flagged</p>
          <p className="text-3xl font-bold text-yellow-400 mt-2">
            {data?.claims_flagged || 0}
          </p>
          <p className="text-xs text-white/30 mt-1">Confidence 60-84</p>
        </motion.div>

        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          <p className="text-sm text-white/50">Rejected</p>
          <p className="text-3xl font-bold text-red-400 mt-2">
            {data?.claims_rejected || 0}
          </p>
          <p className="text-xs text-white/30 mt-1">Confidence &lt; 35</p>
        </motion.div>
      </div>
    </div>
  );
}
