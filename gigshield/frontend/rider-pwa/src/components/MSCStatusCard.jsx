/**
 * MSCStatusCard — Shows current MSC (Multi-Signal Confluence) status.
 * Displays 3 signals with live status indicators.
 */

import React from 'react';

const SIGNAL_CONFIG = {
  rainfall: { icon: '🌧️', label: 'Rainfall', unit: 'mm/hr', threshold: 8.0 },
  aqi: { icon: '💨', label: 'AQI', unit: '', threshold: 200 },
  order_drop: { icon: '📉', label: 'Order Drop', unit: '%', threshold: 35 },
};

const MSC_STATUS_STYLES = {
  not_met: { color: '#94a3b8', bg: 'rgba(148,163,184,0.08)', label: 'Normal' },
  standard: { color: '#eab308', bg: 'rgba(234,179,8,0.08)', label: '2-Signal Disruption' },
  high: { color: '#ef4444', bg: 'rgba(239,68,68,0.08)', label: '3-Signal Disruption' },
};

export default function MSCStatusCard({
  mscStatus = 'not_met',
  signals = {},
  zoneName = 'BTM Layout',
}) {
  const statusStyle = MSC_STATUS_STYLES[mscStatus] || MSC_STATUS_STYLES.not_met;

  const signalData = [
    {
      key: 'rainfall',
      value: signals.rainfall_mm_hr || 0,
      active: (signals.rainfall_mm_hr || 0) >= SIGNAL_CONFIG.rainfall.threshold,
    },
    {
      key: 'aqi',
      value: signals.aqi_value || 0,
      active: (signals.aqi_value || 0) >= SIGNAL_CONFIG.aqi.threshold,
    },
    {
      key: 'order_drop',
      value: signals.order_drop_pct ? (signals.order_drop_pct * 100) : 0,
      active: (signals.order_drop_pct || 0) >= (SIGNAL_CONFIG.order_drop.threshold / 100),
    },
  ];

  const activeCount = signalData.filter(s => s.active).length;

  return (
    <div style={{
      backgroundColor: 'rgba(255,255,255,0.03)',
      borderRadius: 16, padding: 20,
      border: `1px solid ${mscStatus !== 'not_met' ? statusStyle.color : 'rgba(255,255,255,0.06)'}`,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#fff' }}>MSC Status</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>{zoneName}</div>
        </div>
        <div style={{
          padding: '6px 14px', borderRadius: 20,
          backgroundColor: statusStyle.bg, color: statusStyle.color,
          fontSize: 12, fontWeight: 600,
        }}>
          {statusStyle.label}
        </div>
      </div>

      {/* Signal indicators */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {signalData.map(({ key, value, active }) => {
          const config = SIGNAL_CONFIG[key];
          return (
            <div key={key} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '10px 14px', borderRadius: 10,
              backgroundColor: active ? `${statusStyle.color}10` : 'rgba(255,255,255,0.02)',
            }}>
              <span style={{ fontSize: 20 }}>{config.icon}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>{config.label}</div>
                <div style={{ fontSize: 16, fontWeight: 600, color: active ? statusStyle.color : '#fff' }}>
                  {key === 'order_drop' ? `${value.toFixed(0)}%` : value.toFixed(1)}{config.unit && ` ${config.unit}`}
                </div>
              </div>
              <div style={{
                width: 8, height: 8, borderRadius: '50%',
                backgroundColor: active ? '#22c55e' : 'rgba(255,255,255,0.15)',
              }} />
            </div>
          );
        })}
      </div>

      {/* Signal count */}
      <div style={{
        marginTop: 14, textAlign: 'center',
        fontSize: 12, color: 'rgba(255,255,255,0.4)',
      }}>
        {activeCount}/3 signals active
        {activeCount >= 2 && ' — Coverage triggered ✓'}
      </div>
    </div>
  );
}
