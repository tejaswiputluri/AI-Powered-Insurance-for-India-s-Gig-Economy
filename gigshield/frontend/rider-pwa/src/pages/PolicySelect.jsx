/**
 * Policy Selection — choose from 4 tiers.
 * Vertical stack on mobile, recommended badge on Balanced.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { createPolicy } from '../services/api';
import { formatRupees } from '../utils/formatters';
import toast from 'react-hot-toast';

const TIERS = [
  {
    tier: 'basic', name: 'Basic', emoji: '🛡️',
    description: 'Essential cover for light disruptions',
    premium: 2900, cap: 50000, msc: 2, cf: 0.70,
  },
  {
    tier: 'balanced', name: 'Balanced', emoji: '⚖️', recommended: true,
    description: 'Popular choice — good coverage, fair price',
    premium: 6700, cap: 90000, msc: 2, cf: 0.70,
  },
  {
    tier: 'pro', name: 'Pro', emoji: '🚀',
    description: 'Higher coverage with 3-signal boost',
    premium: 7900, cap: 150000, msc: 2, cf: 0.85,
  },
  {
    tier: 'aggressive', name: 'Aggressive', emoji: '💎',
    description: 'Maximum protection — full coverage cap',
    premium: 9900, cap: 220000, msc: 2, cf: 0.85,
  },
];

export default function PolicySelect({ premiumData, onPolicyCreated }) {
  const navigate = useNavigate();
  const [selected, setSelected] = useState('balanced');
  const [loading, setLoading] = useState(false);

  const tiers = premiumData?.tier_options || TIERS;

  async function handleSelect() {
    setLoading(true);
    try {
      console.log('Creating policy with tier:', selected);
      await createPolicy(selected);
      toast.success('Policy activated! 🎉');
      onPolicyCreated?.();
      navigate('/dashboard');
    } catch (err) {
      console.error('Policy creation error:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        detail: err.response?.data?.detail,
        fullData: err.response?.data,
        message: err.message,
      });
      const errMessage = err.response?.data?.detail?.message 
        || err.response?.data?.detail 
        || err.message 
        || 'Failed to create policy';
      toast.error(errMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-navy-500 flex flex-col px-6 py-8">
      <div className="mb-6">
        <button onClick={() => navigate(-1)} className="text-white/40 text-sm mb-4 hover:text-white/60">
          ← Back
        </button>
        <h1 className="text-2xl font-bold">Choose Your Plan</h1>
        <p className="text-white/50 mt-1">All plans include automatic payouts</p>
      </div>

      <div className="space-y-4 mb-6 flex-1">
        {(Array.isArray(tiers) ? tiers : TIERS).map((tier, i) => {
          const t = tier.tier || tier;
          const isSelected = selected === t;
          const isRecommended = tier.recommended;

          return (
            <motion.button
              key={t}
              onClick={() => setSelected(t)}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`w-full glass-card p-5 text-left transition-all relative ${
                isSelected
                  ? 'border-2 border-gold-500 shadow-lg shadow-gold-500/10'
                  : 'border-2 border-transparent hover:border-white/10'
              }`}
            >
              {isRecommended && (
                <span className="absolute -top-3 right-4 bg-gold-500 text-navy-500 text-xs font-bold px-3 py-1 rounded-full">
                  RECOMMENDED
                </span>
              )}

              <div className="flex items-start gap-4">
                <span className="text-3xl">{tier.emoji || '🛡️'}</span>
                <div className="flex-1">
                  <h3 className="text-lg font-bold">{tier.name}</h3>
                  <p className="text-white/40 text-sm mt-1">{tier.description}</p>

                  <div className="flex justify-between mt-3 pt-3 border-t border-white/5">
                    <div>
                      <p className="text-xs text-white/30">Premium</p>
                      <p className="text-gold-500 font-bold">
                        {formatRupees(tier.weekly_premium_paise || tier.premium)}/wk
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-white/30">Max Payout</p>
                      <p className="text-white font-bold">
                        {formatRupees(tier.coverage_cap_paise || tier.cap)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-white/30">Coverage</p>
                      <p className="text-white font-bold">
                        {Math.round((tier.coverage_factor || tier.cf) * 100)}%
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>

      <button
        onClick={handleSelect}
        disabled={loading}
        className="w-full bg-gold-500 text-navy-500 py-4 rounded-xl font-bold text-lg disabled:opacity-50 hover:bg-gold-400 transition-colors"
      >
        {loading ? 'Activating...' : `Activate ${selected.charAt(0).toUpperCase() + selected.slice(1)} Plan ⚡`}
      </button>
    </div>
  );
}
