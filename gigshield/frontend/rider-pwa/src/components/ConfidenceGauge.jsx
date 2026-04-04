/**
 * ConfidenceGauge — SVG circular gauge showing fraud confidence score.
 * Colors: Green (≥85), Yellow (60-84), Orange (35-59), Red (<35)
 * Shows score in center with label underneath.
 */

import React from 'react';

const getGaugeColor = (score) => {
  if (score >= 85) return { stroke: '#22c55e', bg: 'rgba(34, 197, 94, 0.08)', label: 'Verified' };
  if (score >= 60) return { stroke: '#eab308', bg: 'rgba(234, 179, 8, 0.08)', label: 'Flagged' };
  if (score >= 35) return { stroke: '#f97316', bg: 'rgba(249, 115, 22, 0.08)', label: 'Under Review' };
  return { stroke: '#ef4444', bg: 'rgba(239, 68, 68, 0.08)', label: 'Rejected' };
};

export default function ConfidenceGauge({ score = 0, size = 120 }) {
  const { stroke, bg, label } = getGaugeColor(score);
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const center = size / 2;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <div style={{
        position: 'relative', width: size, height: size,
        backgroundColor: bg, borderRadius: '50%',
      }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {/* Background circle */}
          <circle
            cx={center} cy={center} r={radius}
            fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8"
          />
          {/* Progress arc */}
          <circle
            cx={center} cy={center} r={radius}
            fill="none" stroke={stroke} strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${progress} ${circumference}`}
            transform={`rotate(-90 ${center} ${center})`}
            style={{ transition: 'stroke-dasharray 0.8s ease-in-out' }}
          />
        </svg>
        {/* Center text */}
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: size * 0.28, fontWeight: 700, color: stroke }}>{score}</div>
          <div style={{ fontSize: size * 0.1, color: 'rgba(255,255,255,0.5)', marginTop: -4 }}>/100</div>
        </div>
      </div>
      <div style={{
        fontSize: 13, fontWeight: 600, color: stroke,
        padding: '4px 12px', borderRadius: 12,
        backgroundColor: bg,
      }}>
        {label}
      </div>
    </div>
  );
}
