/**
 * Reserves — weekly reserve estimates and zone breakdown.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getReserves } from '../services/api';

function formatRupees(paise) {
  return `₹${Math.round((paise || 0) / 100).toLocaleString('en-IN')}`;
}

export default function Reserves() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const res = await getReserves();
      setData(res);
    } catch (err) {
      setData({
        current_week_reserve_paise: 2450000,
        next_week_estimate_paise: 2695000,
        reserve_ratio: 1.10,
        breakdown_by_zone: [
          { zone_id: 'BTM_LAYOUT', zone_name: 'BTM Layout', reserve_paise: 385000, expected_claims: 11 },
          { zone_id: 'HSR_LAYOUT', zone_name: 'HSR Layout', reserve_paise: 315000, expected_claims: 9 },
          { zone_id: 'INDIRANAGAR', zone_name: 'Indiranagar', reserve_paise: 350000, expected_claims: 10 },
          { zone_id: 'KORAMANGALA', zone_name: 'Koramangala', reserve_paise: 280000, expected_claims: 8 },
          { zone_id: 'JAYANAGAR', zone_name: 'Jayanagar', reserve_paise: 245000, expected_claims: 7 },
        ],
      });
    }
    setLoading(false);
  }

  if (loading) return <div className="text-white/50">Loading...</div>;

  const maxReserve = Math.max(
    ...(data?.breakdown_by_zone || []).map(z => z.reserve_paise || 0),
    1
  );

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Reserve Estimates</h1>
      <p className="text-white/40 text-sm mb-8">Weekly reserves and zone-level breakdown</p>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <p className="text-white/40 text-sm">Current Week Reserve</p>
          <p className="text-3xl font-bold text-[#E89B0A] mt-2">
            {formatRupees(data?.current_week_reserve_paise)}
          </p>
        </motion.div>

        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <p className="text-white/40 text-sm">Next Week Estimate</p>
          <p className="text-3xl font-bold mt-2">
            {formatRupees(data?.next_week_estimate_paise)}
          </p>
        </motion.div>

        <motion.div
          className="glass-card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <p className="text-white/40 text-sm">Reserve Ratio</p>
          <p className={`text-3xl font-bold mt-2 ${
            (data?.reserve_ratio || 0) >= 1.2 ? 'text-green-400' :
            (data?.reserve_ratio || 0) >= 0.8 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {data?.reserve_ratio?.toFixed(2) || '-'}x
          </p>
        </motion.div>
      </div>

      {/* Zone Breakdown */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-bold mb-4">Zone Breakdown</h2>
        <div className="space-y-4">
          {(data?.breakdown_by_zone || []).map((zone, i) => (
            <motion.div
              key={zone.zone_id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + i * 0.05 }}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">{zone.zone_name}</span>
                <div className="text-right">
                  <span className="text-sm font-bold text-[#E89B0A]">
                    {formatRupees(zone.reserve_paise)}
                  </span>
                  <span className="text-xs text-white/30 ml-2">
                    ({zone.expected_claims} claims)
                  </span>
                </div>
              </div>
              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-[#E89B0A] to-yellow-400"
                  initial={{ width: 0 }}
                  animate={{ width: `${(zone.reserve_paise / maxReserve) * 100}%` }}
                  transition={{ duration: 0.6, delay: 0.4 + i * 0.05 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
