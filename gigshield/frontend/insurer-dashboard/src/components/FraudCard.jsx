/**
 * FraudCard — Individual fraud queue item card.
 * Shows claim details, 4-layer fraud scores, and approve/reject buttons.
 */

import React, { useState } from 'react';

function formatPaise(paise) {
  if (paise == null) return '₹0';
  return `₹${Math.round(paise / 100).toLocaleString('en-IN')}`;
}

const LAYER_CONFIG = {
  l1_gps: { label: 'L1: GPS', icon: '📍', max: 30 },
  l2_weather: { label: 'L2: Weather', icon: '🌧️', max: 30 },
  l3_earnings: { label: 'L3: Earnings', icon: '📊', max: 25 },
  l4_cluster: { label: 'L4: Cluster', icon: '🔗', max: 15 },
};

export default function FraudCard({ item, onDecision }) {
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDecision = async (decision) => {
    setLoading(true);
    try {
      await onDecision(item.claim_id, decision, note);
    } finally {
      setLoading(false);
    }
  };

  const layers = [
    { key: 'l1_gps', score: item.l1_gps_score, result: item.l1_gps_result },
    { key: 'l2_weather', score: item.l2_weather_score, result: item.l2_weather_result },
    { key: 'l3_earnings', score: item.l3_earnings_score, result: item.l3_earnings_result },
    { key: 'l4_cluster', score: item.l4_cluster_score, result: item.l4_cluster_result },
  ];

  return (
    <div style={{
      backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 14,
      border: '1px solid rgba(255,255,255,0.08)', padding: 20, marginBottom: 12,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#fff' }}>
            {item.rider_name}
          </div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>
            {item.zone_id} · {item.time_waiting_minutes}min waiting
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 18, fontWeight: 700, color: '#eab308' }}>
            {item.confidence_score}/100
          </div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)' }}>
            {formatPaise(item.claim_amount_paise)}
          </div>
        </div>
      </div>

      {/* 4-Layer breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 14 }}>
        {layers.map(({ key, score, result }) => {
          const config = LAYER_CONFIG[key];
          const pct = (score / config.max) * 100;
          const color = result === 'pass' ? '#22c55e' : result === 'fail' ? '#ef4444' : '#94a3b8';

          return (
            <div key={key} style={{
              padding: '8px 10px', borderRadius: 8,
              backgroundColor: `${color}08`, borderLeft: `3px solid ${color}`,
            }}>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)' }}>
                {config.icon} {config.label}
              </div>
              <div style={{ fontSize: 14, fontWeight: 600, color }}>
                {score}/{config.max} {result === 'skip' ? '(skip)' : ''}
              </div>
            </div>
          );
        })}
      </div>

      {/* Note input */}
      <input
        type="text"
        placeholder="Add note (optional)..."
        value={note}
        onChange={(e) => setNote(e.target.value)}
        style={{
          width: '100%', padding: '8px 12px', borderRadius: 8,
          backgroundColor: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
          color: '#fff', fontSize: 12, marginBottom: 12, outline: 'none',
          boxSizing: 'border-box',
        }}
      />

      {/* Actions */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button
          onClick={() => handleDecision('approve')}
          disabled={loading}
          style={{
            flex: 1, padding: '10px 16px', borderRadius: 10,
            backgroundColor: 'rgba(34,197,94,0.15)', border: '1px solid #22c55e',
            color: '#22c55e', cursor: 'pointer', fontWeight: 600, fontSize: 13,
          }}
        >
          ✓ Approve
        </button>
        <button
          onClick={() => handleDecision('reject')}
          disabled={loading}
          style={{
            flex: 1, padding: '10px 16px', borderRadius: 10,
            backgroundColor: 'rgba(239,68,68,0.15)', border: '1px solid #ef4444',
            color: '#ef4444', cursor: 'pointer', fontWeight: 600, fontSize: 13,
          }}
        >
          ✕ Reject
        </button>
      </div>
    </div>
  );
}
