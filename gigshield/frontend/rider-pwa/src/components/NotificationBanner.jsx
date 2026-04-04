/**
 * NotificationBanner — Toast notification banner for real-time updates.
 * Displays SMS-style notifications from the notification service.
 */

import React, { useState, useEffect } from 'react';

const TYPE_STYLES = {
  PAYOUT_SENT: { icon: '💸', bg: 'rgba(34,197,94,0.12)', border: '#22c55e' },
  DISRUPTION_DETECTED: { icon: '⚡', bg: 'rgba(234,179,8,0.12)', border: '#eab308' },
  CLAIM_REJECTED: { icon: '❌', bg: 'rgba(239,68,68,0.12)', border: '#ef4444' },
  CLAIM_ON_HOLD: { icon: '⏳', bg: 'rgba(249,115,22,0.12)', border: '#f97316' },
  WEEKLY_COVERAGE_SUMMARY: { icon: '📋', bg: 'rgba(99,102,241,0.12)', border: '#6366f1' },
  PRE_DISRUPTION_WARNING: { icon: '⚠️', bg: 'rgba(234,179,8,0.12)', border: '#eab308' },
};

export default function NotificationBanner({ notification, onDismiss, autoHideMs = 8000 }) {
  const [visible, setVisible] = useState(true);
  const style = TYPE_STYLES[notification?.type] || TYPE_STYLES.WEEKLY_COVERAGE_SUMMARY;

  useEffect(() => {
    if (autoHideMs > 0) {
      const timer = setTimeout(() => {
        setVisible(false);
        setTimeout(() => onDismiss?.(), 300);
      }, autoHideMs);
      return () => clearTimeout(timer);
    }
  }, [autoHideMs, onDismiss]);

  if (!notification || !visible) return null;

  return (
    <div style={{
      position: 'fixed', top: 16, left: 16, right: 16, zIndex: 1000,
      backgroundColor: style.bg, borderRadius: 14,
      border: `1px solid ${style.border}`,
      padding: '14px 16px',
      display: 'flex', alignItems: 'flex-start', gap: 12,
      backdropFilter: 'blur(20px)',
      animation: visible ? 'slideDown 0.3s ease-out' : 'slideUp 0.3s ease-in',
      boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
    }}>
      <span style={{ fontSize: 24 }}>{style.icon}</span>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#fff', marginBottom: 4 }}>
          GigShield
        </div>
        <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', lineHeight: 1.4 }}>
          {notification.message}
        </div>
      </div>
      <button
        onClick={() => { setVisible(false); onDismiss?.(); }}
        style={{
          background: 'none', border: 'none', color: 'rgba(255,255,255,0.4)',
          cursor: 'pointer', fontSize: 16, padding: 4,
        }}
      >
        ✕
      </button>
    </div>
  );
}
