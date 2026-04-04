/**
 * Coverage Simulator — preview payouts for different scenarios.
 * Live-updating as slider moves.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { simulateCoverage } from '../services/api';
import { formatRupees } from '../utils/formatters';

export default function Simulator() {
  const navigate = useNavigate();
  const [hours, setHours] = useState(4);
  const [signals, setSignals] = useState(2);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSimulation();
  }, [hours, signals]);

  async function fetchSimulation() {
    setLoading(true);
    try {
      const res = await simulateCoverage({
        zone_id: 'BTM_LAYOUT',
        disruption_hours: hours,
        signal_count: signals,
      });
      setResult(res);
    } catch (err) {
      // Use fallback calculation
      const bhe = Math.round(110000 / 12);
      const zif = 0.87;
      const cf = signals >= 3 ? 0.85 : 0.70;
      const payout = Math.round(bhe * hours * zif * cf);
      setResult({
        estimated_payout_paise: Math.min(payout, 90000),
        breakdown: {
          baseline_hourly_paise: bhe,
          disruption_hours: hours,
          zone_impact_factor: zif,
          coverage_factor: cf,
        },
      });
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-navy-500 flex flex-col px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <button onClick={() => navigate(-1)} className="text-white/40 text-sm mb-4 hover:text-white/60">
          ← Back
        </button>
        <h1 className="text-2xl font-bold">Coverage Simulator</h1>
        <p className="text-white/50 mt-1">See what you'd get paid</p>
      </div>

      {/* Controls */}
      <div className="glass-card p-6 mb-6">
        <div className="mb-6">
          <label className="text-white/60 text-sm block mb-3">
            Disruption Duration:
            <span className="text-gold-500 font-bold text-lg ml-2">{hours} hours</span>
          </label>
          <input
            type="range"
            min="1" max="8" step="1"
            value={hours}
            onChange={(e) => setHours(parseInt(e.target.value))}
            className="w-full accent-gold-500"
          />
          <div className="flex justify-between text-xs text-white/30 mt-1">
            <span>1 hr</span><span>8 hrs (max)</span>
          </div>
        </div>

        <div>
          <label className="text-white/60 text-sm block mb-3">Signal Strength</label>
          <div className="flex gap-3">
            <button
              onClick={() => setSignals(2)}
              className={`flex-1 py-3 rounded-xl font-medium transition-all ${
                signals === 2
                  ? 'bg-gold-500/20 border-2 border-gold-500 text-gold-500'
                  : 'bg-white/5 border-2 border-transparent text-white/50'
              }`}
            >
              2 Signals (70%)
            </button>
            <button
              onClick={() => setSignals(3)}
              className={`flex-1 py-3 rounded-xl font-medium transition-all ${
                signals === 3
                  ? 'bg-gold-500/20 border-2 border-gold-500 text-gold-500'
                  : 'bg-white/5 border-2 border-transparent text-white/50'
              }`}
            >
              3 Signals (85%)
            </button>
          </div>
        </div>
      </div>

      {/* Result */}
      {result && (
        <motion.div
          className="glass-card p-6 mb-6"
          key={`${hours}-${signals}`}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <p className="text-white/50 text-sm mb-2">
            If disruption lasts {hours} hours...
          </p>
          <h2 className="text-5xl font-extrabold gold-gradient mb-6">
            {formatRupees(result.estimated_payout_paise)}
          </h2>

          {/* Breakdown */}
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-white/50">Baseline hourly</span>
              <span className="text-white font-medium">
                {formatRupees(result.breakdown.baseline_hourly_paise)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">× Disruption hours</span>
              <span className="text-white font-medium">{result.breakdown.disruption_hours}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">× Zone factor</span>
              <span className="text-white font-medium">{result.breakdown.zone_impact_factor}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">× Coverage</span>
              <span className="text-white font-medium">
                {Math.round(result.breakdown.coverage_factor * 100)}%
              </span>
            </div>
            <div className="h-px bg-white/10 my-2" />
            <div className="flex justify-between items-center">
              <span className="text-white/60 text-xs">BHE × DW × ZIF × CF</span>
              <span className="text-gold-500 font-bold text-lg">
                = {formatRupees(result.estimated_payout_paise)}
              </span>
            </div>
          </div>
        </motion.div>
      )}

      {/* CTA */}
      <div className="mt-auto">
        <button
          onClick={() => navigate('/select-policy')}
          className="w-full bg-gold-500 text-navy-500 py-4 rounded-xl font-bold text-lg hover:bg-gold-400 transition-colors"
        >
          Get Covered →
        </button>
      </div>
    </div>
  );
}
