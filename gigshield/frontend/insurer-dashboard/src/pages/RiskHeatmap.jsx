/**
 * Risk Heatmap — Bengaluru zone map with disruption probability.
 * Uses Leaflet.js for the map visualization.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getHeatmap } from '../services/api';

// Fallback data in case API is not available
const MOCK_ZONES = [
  { zone_id: 'BTM_LAYOUT', zone_name: 'BTM Layout', lat: 12.9165, lon: 77.6101, disruption_probability: 0.73, expected_claims: 11, reserve_estimate_paise: 385000, risk_level: 'high' },
  { zone_id: 'KORAMANGALA', zone_name: 'Koramangala', lat: 12.9352, lon: 77.6245, disruption_probability: 0.55, expected_claims: 8, reserve_estimate_paise: 280000, risk_level: 'medium' },
  { zone_id: 'INDIRANAGAR', zone_name: 'Indiranagar', lat: 12.9716, lon: 77.6412, disruption_probability: 0.68, expected_claims: 10, reserve_estimate_paise: 350000, risk_level: 'high' },
  { zone_id: 'WHITEFIELD', zone_name: 'Whitefield', lat: 12.9698, lon: 77.7500, disruption_probability: 0.42, expected_claims: 6, reserve_estimate_paise: 210000, risk_level: 'medium' },
  { zone_id: 'JAYANAGAR', zone_name: 'Jayanagar', lat: 12.9250, lon: 77.5938, disruption_probability: 0.50, expected_claims: 7, reserve_estimate_paise: 245000, risk_level: 'medium' },
  { zone_id: 'MARATHAHALLI', zone_name: 'Marathahalli', lat: 12.9591, lon: 77.6974, disruption_probability: 0.38, expected_claims: 5, reserve_estimate_paise: 175000, risk_level: 'medium' },
  { zone_id: 'HSR_LAYOUT', zone_name: 'HSR Layout', lat: 12.9081, lon: 77.6476, disruption_probability: 0.65, expected_claims: 9, reserve_estimate_paise: 315000, risk_level: 'high' },
  { zone_id: 'ELECTRONIC_CITY', zone_name: 'Electronic City', lat: 12.8399, lon: 77.6770, disruption_probability: 0.30, expected_claims: 4, reserve_estimate_paise: 140000, risk_level: 'low' },
  { zone_id: 'HEBBAL', zone_name: 'Hebbal', lat: 13.0358, lon: 77.5970, disruption_probability: 0.48, expected_claims: 7, reserve_estimate_paise: 245000, risk_level: 'medium' },
  { zone_id: 'JP_NAGAR', zone_name: 'JP Nagar', lat: 12.9063, lon: 77.5857, disruption_probability: 0.45, expected_claims: 6, reserve_estimate_paise: 210000, risk_level: 'medium' },
];

const riskColors = {
  high: { bg: 'bg-red-500/20', text: 'text-red-400', dot: 'bg-red-500' },
  medium: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', dot: 'bg-yellow-500' },
  low: { bg: 'bg-green-500/20', text: 'text-green-400', dot: 'bg-green-500' },
};

export default function RiskHeatmap() {
  const [zones, setZones] = useState(MOCK_ZONES);
  const [selectedZone, setSelectedZone] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const res = await getHeatmap();
      if (res.zones?.length > 0) setZones(res.zones);
    } catch (err) {
      // Use mock data
    }
  }

  const sortedZones = [...zones].sort((a, b) => b.disruption_probability - a.disruption_probability);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Risk Heatmap</h1>
      <p className="text-white/40 text-sm mb-8">LSTM-predicted disruption probability by zone</p>

      <div className="grid grid-cols-3 gap-4">
        {/* Zone List */}
        <div className="col-span-1 space-y-2">
          {sortedZones.map((zone, i) => {
            const risk = riskColors[zone.risk_level] || riskColors.medium;
            return (
              <motion.button
                key={zone.zone_id}
                onClick={() => setSelectedZone(zone)}
                className={`w-full glass-card p-4 text-left hover:bg-white/5 transition-colors ${
                  selectedZone?.zone_id === zone.zone_id ? 'border border-[#E89B0A]/50' : ''
                }`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${risk.dot}`} />
                    <span className="font-medium text-sm">{zone.zone_name}</span>
                  </div>
                  <span className={`text-sm font-bold ${risk.text}`}>
                    {Math.round(zone.disruption_probability * 100)}%
                  </span>
                </div>
              </motion.button>
            );
          })}
        </div>

        {/* Map Placeholder / Selected Zone Detail */}
        <div className="col-span-2">
          {selectedZone ? (
            <motion.div
              className="glass-card p-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <h2 className="text-2xl font-bold mb-4">{selectedZone.zone_name}</h2>

              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-white/5 rounded-xl p-4">
                  <p className="text-white/40 text-sm">Disruption Prob.</p>
                  <p className="text-2xl font-bold text-[#E89B0A] mt-1">
                    {Math.round(selectedZone.disruption_probability * 100)}%
                  </p>
                </div>
                <div className="bg-white/5 rounded-xl p-4">
                  <p className="text-white/40 text-sm">Expected Claims</p>
                  <p className="text-2xl font-bold mt-1">{selectedZone.expected_claims}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4">
                  <p className="text-white/40 text-sm">Reserve Estimate</p>
                  <p className="text-2xl font-bold mt-1">
                    ₹{Math.round(selectedZone.reserve_estimate_paise / 100).toLocaleString('en-IN')}
                  </p>
                </div>
              </div>

              {/* Risk gauge */}
              <div className="mb-4">
                <p className="text-white/40 text-sm mb-2">Risk Level</p>
                <div className="h-4 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full rounded-full ${
                      selectedZone.risk_level === 'high' ? 'bg-red-500' :
                      selectedZone.risk_level === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${selectedZone.disruption_probability * 100}%` }}
                    transition={{ duration: 0.6 }}
                  />
                </div>
              </div>

              <p className="text-white/30 text-xs">
                Coordinates: ({selectedZone.lat.toFixed(4)}, {selectedZone.lon.toFixed(4)})
              </p>
            </motion.div>
          ) : (
            <div className="glass-card p-12 text-center">
              <span className="text-4xl block mb-4">🗺️</span>
              <p className="text-white/50">Select a zone to view details</p>
              <p className="text-white/30 text-sm mt-2">
                Zone probabilities are updated weekly by the LSTM forecast model
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
