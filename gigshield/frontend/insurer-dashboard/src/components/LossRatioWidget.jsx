/**
 * LossRatioWidget — Displays premium collected vs claims paid with loss ratio.
 * Used in the insurer dashboard overview.
 */

import React from 'react';

function formatPaise(paise) {
  if (paise == null) return '₹0';
  const rupees = paise / 100;
  if (rupees >= 100000) return `₹${(rupees / 100000).toFixed(1)}L`;
  if (rupees >= 1000) return `₹${(rupees / 1000).toFixed(1)}K`;
  return `₹${rupees.toLocaleString('en-IN')}`;
}

export default function LossRatioWidget({ premiumPaise = 0, claimsPaidPaise = 0, lossRatio = 0 }) {
  const ratioColor = lossRatio > 1.0 ? '#ef4444' : lossRatio > 0.7 ? '#eab308' : '#22c55e';
  const ratioPercent = Math.min(lossRatio * 100, 150);

  return (
    <div style={{
      backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 16, padding: 20,
      border: '1px solid rgba(255,255,255,0.06)',
    }}>
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', marginBottom: 12 }}>
        Loss Ratio
      </div>
      <div style={{ fontSize: 32, fontWeight: 700, color: ratioColor, marginBottom: 16 }}>
        {(lossRatio * 100).toFixed(1)}%
      </div>

      {/* Bar */}
      <div style={{ height: 8, backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 4, marginBottom: 16 }}>
        <div style={{
          height: '100%', width: `${Math.min(ratioPercent, 100)}%`,
          backgroundColor: ratioColor, borderRadius: 4,
          transition: 'width 0.8s ease',
        }} />
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
        <div>
          <div style={{ color: 'rgba(255,255,255,0.4)' }}>Premium</div>
          <div style={{ color: '#22c55e', fontWeight: 600 }}>{formatPaise(premiumPaise)}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ color: 'rgba(255,255,255,0.4)' }}>Claims Paid</div>
          <div style={{ color: '#ef4444', fontWeight: 600 }}>{formatPaise(claimsPaidPaise)}</div>
        </div>
      </div>
    </div>
  );
}
