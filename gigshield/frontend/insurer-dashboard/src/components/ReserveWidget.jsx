/**
 * ReserveWidget — Weekly reserve summary card with zone breakdown.
 */

import React from 'react';

function formatPaise(paise) {
  if (paise == null) return '₹0';
  const rupees = paise / 100;
  if (rupees >= 100000) return `₹${(rupees / 100000).toFixed(1)}L`;
  if (rupees >= 1000) return `₹${(rupees / 1000).toFixed(1)}K`;
  return `₹${rupees.toLocaleString('en-IN')}`;
}

export default function ReserveWidget({ currentWeekPaise, nextWeekPaise, reserveRatio, breakdown = [] }) {
  const ratioColor = reserveRatio > 1.0 ? '#ef4444' : '#22c55e';

  return (
    <div style={{
      backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 16, padding: 20,
      border: '1px solid rgba(255,255,255,0.06)',
    }}>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', marginBottom: 12 }}>
        📦 Reserve Estimates
      </div>

      <div style={{ display: 'flex', gap: 20, marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>This Week</div>
          <div style={{ fontSize: 20, fontWeight: 700, color: '#fff' }}>
            {formatPaise(currentWeekPaise)}
          </div>
        </div>
        <div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>Next Week Est.</div>
          <div style={{ fontSize: 20, fontWeight: 700, color: ratioColor }}>
            {formatPaise(nextWeekPaise)}
          </div>
        </div>
      </div>

      {/* Top zones */}
      {breakdown.slice(0, 5).map(zone => (
        <div key={zone.zone_id} style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '6px 0', borderBottom: '1px solid rgba(255,255,255,0.04)',
          fontSize: 12,
        }}>
          <span style={{ color: 'rgba(255,255,255,0.6)' }}>{zone.zone_name}</span>
          <span style={{ color: '#818cf8', fontWeight: 600 }}>{formatPaise(zone.reserve_paise)}</span>
        </div>
      ))}
    </div>
  );
}
