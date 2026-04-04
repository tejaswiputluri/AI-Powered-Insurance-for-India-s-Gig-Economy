/**
 * XAIPanel — Explainable AI attention weight visualization.
 * Shows how the FT-Transformer weighted each factor for premium calculation.
 */

import React from 'react';

const FACTOR_ICONS = {
  aqi_zone_history: '💨',
  monsoon_season: '🌧️',
  zone_risk_score: '📍',
  claim_history: '📊',
};

const FACTOR_DESCRIPTIONS = {
  aqi_zone_history: 'How polluted your zone has been historically',
  monsoon_season: 'Current monsoon season intensity',
  zone_risk_score: 'Overall disruption risk in your zone',
  claim_history: 'Your past claim patterns',
};

export default function XAIPanel({ factors = [] }) {
  const maxWeight = Math.max(...factors.map(f => f.weight), 0.01);

  return (
    <div style={{
      backgroundColor: 'rgba(255,255,255,0.03)',
      borderRadius: 16, padding: 20,
    }}>
      <div style={{ fontSize: 14, fontWeight: 600, color: '#fff', marginBottom: 4 }}>
        Why this premium?
      </div>
      <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 16 }}>
        AI attention weights for your risk profile
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {factors.map((factor, i) => {
          const icon = FACTOR_ICONS[factor.factor] || '📊';
          const desc = FACTOR_DESCRIPTIONS[factor.factor] || '';
          const barWidth = (factor.weight / maxWeight) * 100;

          return (
            <div key={factor.factor}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ fontSize: 13, color: '#fff' }}>
                  {icon} {factor.label}
                </span>
                <span style={{ fontSize: 13, fontWeight: 600, color: '#818cf8' }}>
                  {(factor.weight * 100).toFixed(0)}%
                </span>
              </div>
              <div style={{
                height: 6, backgroundColor: 'rgba(255,255,255,0.06)',
                borderRadius: 3, overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%', width: `${barWidth}%`,
                  background: 'linear-gradient(90deg, #818cf8, #6366f1)',
                  borderRadius: 3,
                  transition: 'width 0.6s ease-out',
                }} />
              </div>
              {desc && (
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginTop: 2 }}>
                  {desc}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
