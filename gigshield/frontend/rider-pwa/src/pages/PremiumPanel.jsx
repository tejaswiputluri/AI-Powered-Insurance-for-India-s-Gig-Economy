/**
 * Premium Panel — shows ML-calculated premium with XAI breakdown.
 * Animated bar chart showing attention weight factors.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { formatRupees } from '../utils/formatters';

export default function PremiumPanel({ premiumData }) {
  const navigate = useNavigate();

  // Default/demo data if none provided
  const data = premiumData || {
    computed_premium_paise: 6700,
    xai_factors: [
      { factor: 'aqi_zone_history', weight: 0.34, label: 'AQI Zone History' },
      { factor: 'monsoon_season', weight: 0.27, label: 'Monsoon Season' },
      { factor: 'zone_risk_score', weight: 0.21, label: 'Zone Risk Score' },
      { factor: 'claim_history', weight: 0.18, label: 'Claim History' },
    ],
  };

  const premium = data.computed_premium_paise || 6700;
  const factors = data.xai_factors || [];

  const maxWeight = Math.max(...factors.map(f => f.weight), 0.01);

  const factorDescriptions = {
    aqi_zone_history: 'Your zone has historically had high air pollution during certain months. This affects your risk profile.',
    monsoon_season: 'Monsoon season brings more rainfall disruptions, increasing the probability of payouts.',
    zone_risk_score: 'Your delivery zone has specific risk characteristics based on terrain and infrastructure.',
    claim_history: 'Your past claims history (if any) contributes to your personalized premium.',
  };

  return (
    <div className="min-h-screen bg-navy-500 flex flex-col px-6 py-8">
      {/* Header */}
      <motion.div
        className="text-center mb-10"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <p className="text-white/50 text-sm mb-2 uppercase tracking-wider">Your personalized premium</p>
        <h1 className="text-6xl font-extrabold gold-gradient mb-2">
          {formatRupees(premium)}
        </h1>
        <p className="text-white/50 text-lg">per week</p>
      </motion.div>

      {/* AI badge */}
      <motion.div
        className="glass-card p-3 mb-8 flex items-center gap-3"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="w-10 h-10 bg-gold-500/20 rounded-full flex items-center justify-center text-lg">
          🧠
        </div>
        <div>
          <p className="text-sm font-semibold text-white">AI-Calculated Premium</p>
          <p className="text-xs text-white/40">FT-Transformer Model · 7 risk factors analyzed</p>
        </div>
      </motion.div>

      {/* XAI Factor Bars */}
      <div className="mb-8">
        <h3 className="text-white/60 text-sm font-medium mb-4 uppercase tracking-wider">
          What drives your premium
        </h3>
        <div className="space-y-4">
          {factors.map((factor, i) => (
            <motion.div
              key={factor.factor}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
            >
              <div className="flex justify-between mb-1">
                <span className="text-white/80 text-sm font-medium">{factor.label}</span>
                <span className="text-gold-500 font-bold text-sm">
                  {Math.round(factor.weight * 100)}%
                </span>
              </div>
              <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-gold-600 to-gold-400"
                  initial={{ width: 0 }}
                  animate={{ width: `${(factor.weight / maxWeight) * 100}%` }}
                  transition={{ duration: 0.6, delay: 0.6 + i * 0.1 }}
                />
              </div>
              <p className="text-white/30 text-xs mt-1">
                {factorDescriptions[factor.factor] || ''}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* CTAs */}
      <div className="mt-auto space-y-3">
        <button
          onClick={() => navigate('/simulator')}
          className="w-full bg-gold-500 text-navy-500 py-4 rounded-xl font-bold text-lg hover:bg-gold-400 transition-colors"
        >
          This looks right ✓
        </button>
        <button
          onClick={() => navigate('/simulator')}
          className="w-full bg-white/5 text-white/60 py-3 rounded-xl font-medium hover:bg-white/10 transition-colors"
        >
          Simulate my coverage →
        </button>
      </div>
    </div>
  );
}
