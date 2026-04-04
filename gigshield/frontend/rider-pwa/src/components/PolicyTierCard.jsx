/**
 * PolicyTierCard — Displays a single policy tier option.
 * Used in the tier selection flow during onboarding.
 */

import React from 'react';
import { formatRupees } from '../utils/formatters';

const TIER_COLORS = {
  basic: { bg: 'rgba(148,163,184,0.08)', border: '#64748b', accent: '#94a3b8' },
  balanced: { bg: 'rgba(99,102,241,0.08)', border: '#6366f1', accent: '#818cf8' },
  pro: { bg: 'rgba(234,179,8,0.08)', border: '#eab308', accent: '#fbbf24' },
  aggressive: { bg: 'rgba(239,68,68,0.08)', border: '#ef4444', accent: '#f87171' },
};

const TIER_ICONS = {
  basic: '🛡️', balanced: '⚖️', pro: '🚀', aggressive: '🔥',
};

export default function PolicyTierCard({ tier, selected, onSelect }) {
  const colors = TIER_COLORS[tier.tier] || TIER_COLORS.basic;
  const icon = TIER_ICONS[tier.tier] || '🛡️';
  const isSelected = selected === tier.tier;

  return (
    <button
      onClick={() => onSelect(tier.tier)}
      style={{
        width: '100%', padding: 16, borderRadius: 14,
        backgroundColor: isSelected ? colors.bg : 'rgba(255,255,255,0.02)',
        border: `2px solid ${isSelected ? colors.border : 'rgba(255,255,255,0.06)'}`,
        cursor: 'pointer', textAlign: 'left',
        transition: 'all 0.2s ease',
        position: 'relative', overflow: 'hidden',
      }}
    >
      {tier.recommended && (
        <div style={{
          position: 'absolute', top: 8, right: 8,
          fontSize: 10, fontWeight: 700, color: '#fff',
          backgroundColor: '#6366f1', padding: '2px 8px',
          borderRadius: 10,
        }}>
          RECOMMENDED
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
        <span style={{ fontSize: 28 }}>{icon}</span>
        <div>
          <div style={{ fontSize: 16, fontWeight: 700, color: '#fff', textTransform: 'capitalize' }}>
            {tier.tier}
          </div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>
            {formatRupees(tier.weekly_premium_paise)}/week
          </div>
        </div>
      </div>

      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8,
        fontSize: 12, color: 'rgba(255,255,255,0.6)',
      }}>
        <div>
          <span style={{ color: 'rgba(255,255,255,0.3)' }}>Coverage: </span>
          <span style={{ color: colors.accent, fontWeight: 600 }}>
            {formatRupees(tier.coverage_cap_paise)}
          </span>
        </div>
        <div>
          <span style={{ color: 'rgba(255,255,255,0.3)' }}>Signals: </span>
          <span style={{ fontWeight: 600 }}>{tier.msc_threshold}+</span>
        </div>
      </div>
    </button>
  );
}
