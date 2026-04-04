/**
 * ClaimTimeline — Vertical timeline showing claim lifecycle events.
 * Events: rain_detected → aqi_confirmed → msc_confirmed → fraud_check → payout_sent
 */

import React from 'react';
import { formatIST } from '../utils/formatters';

const EVENT_ICONS = {
  rain_detected: '🌧️',
  aqi_confirmed: '💨',
  order_drop_confirmed: '📉',
  msc_confirmed: '✅',
  claim_created: '📋',
  fraud_check_completed: '🔍',
  fraud_decision: '⚖️',
  payout_initiated: '💸',
  payout_sent: '✅',
  claim_rejected: '❌',
};

const EVENT_COLORS = {
  rain_detected: '#60a5fa',
  aqi_confirmed: '#a78bfa',
  order_drop_confirmed: '#f59e0b',
  msc_confirmed: '#22c55e',
  claim_created: '#60a5fa',
  fraud_check_completed: '#818cf8',
  fraud_decision: '#f97316',
  payout_initiated: '#22c55e',
  payout_sent: '#22c55e',
  claim_rejected: '#ef4444',
};

export default function ClaimTimeline({ events = [] }) {
  if (!events.length) {
    return (
      <div style={{ textAlign: 'center', padding: 24, color: 'rgba(255,255,255,0.4)' }}>
        No timeline events yet
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', paddingLeft: 32 }}>
      {/* Vertical line */}
      <div style={{
        position: 'absolute', left: 11, top: 8, bottom: 8,
        width: 2, backgroundColor: 'rgba(255,255,255,0.1)',
      }} />

      {events.map((event, i) => {
        const color = EVENT_COLORS[event.event] || '#94a3b8';
        const icon = EVENT_ICONS[event.event] || '•';
        const isLast = i === events.length - 1;

        return (
          <div key={i} style={{
            position: 'relative', paddingBottom: isLast ? 0 : 20,
          }}>
            {/* Dot on timeline */}
            <div style={{
              position: 'absolute', left: -28, top: 4,
              width: 14, height: 14, borderRadius: '50%',
              backgroundColor: color, border: '2px solid rgba(0,0,0,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 8,
            }} />

            {/* Event content */}
            <div style={{
              backgroundColor: 'rgba(255,255,255,0.03)',
              borderRadius: 8, padding: '10px 14px',
              borderLeft: `3px solid ${color}`,
            }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between',
                alignItems: 'center', marginBottom: 4,
              }}>
                <span style={{ fontSize: 13, fontWeight: 600, color }}>
                  {icon} {event.event.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                </span>
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>
                  {formatIST(event.timestamp)}
                </span>
              </div>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>
                {event.detail}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
