/**
 * BengaluruMap — Bengaluru zone risk heatmap component.
 * Renders an HTML Canvas-based map of Bengaluru zones with color-coded risk levels.
 * Phase 2: Replace with Leaflet.js for interactive mapping.
 */

import React, { useRef, useEffect } from 'react';

const ZONE_POSITIONS = {
  'BTM_LAYOUT':      { x: 0.42, y: 0.62 },
  'KORAMANGALA':     { x: 0.48, y: 0.52 },
  'INDIRANAGAR':     { x: 0.55, y: 0.42 },
  'WHITEFIELD':      { x: 0.85, y: 0.40 },
  'JAYANAGAR':       { x: 0.35, y: 0.55 },
  'MARATHAHALLI':    { x: 0.70, y: 0.45 },
  'HSR_LAYOUT':      { x: 0.50, y: 0.68 },
  'ELECTRONIC_CITY': { x: 0.45, y: 0.88 },
  'HEBBAL':          { x: 0.40, y: 0.15 },
  'JP_NAGAR':        { x: 0.32, y: 0.72 },
};

const RISK_COLORS = {
  high:   { fill: 'rgba(239, 68, 68, 0.3)', stroke: '#ef4444' },
  medium: { fill: 'rgba(234, 179, 8, 0.3)', stroke: '#eab308' },
  low:    { fill: 'rgba(34, 197, 94, 0.3)', stroke: '#22c55e' },
};

export default function BengaluruMap({ zones = [], width = 400, height = 450 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Clear
    ctx.clearRect(0, 0, width, height);

    // Background
    ctx.fillStyle = 'rgba(255,255,255,0.02)';
    ctx.fillRect(0, 0, width, height);

    // City outline (simplified polygon)
    ctx.beginPath();
    ctx.moveTo(width * 0.3, height * 0.05);
    ctx.lineTo(width * 0.7, height * 0.05);
    ctx.lineTo(width * 0.9, height * 0.3);
    ctx.lineTo(width * 0.95, height * 0.6);
    ctx.lineTo(width * 0.8, height * 0.85);
    ctx.lineTo(width * 0.5, height * 0.95);
    ctx.lineTo(width * 0.2, height * 0.85);
    ctx.lineTo(width * 0.1, height * 0.5);
    ctx.lineTo(width * 0.15, height * 0.2);
    ctx.closePath();
    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Draw zones
    zones.forEach(zone => {
      const pos = ZONE_POSITIONS[zone.zone_id];
      if (!pos) return;

      const x = pos.x * width;
      const y = pos.y * height;
      const colors = RISK_COLORS[zone.risk_level] || RISK_COLORS.low;
      const radius = 20 + (zone.disruption_probability * 25);

      // Glow circle
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius * 1.5);
      gradient.addColorStop(0, colors.fill);
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.fillRect(x - radius * 1.5, y - radius * 1.5, radius * 3, radius * 3);

      // Inner circle
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = colors.fill;
      ctx.fill();
      ctx.strokeStyle = colors.stroke;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Zone name
      ctx.fillStyle = '#fff';
      ctx.font = '10px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(zone.zone_name, x, y - radius - 6);

      // Probability
      ctx.fillStyle = colors.stroke;
      ctx.font = 'bold 12px Inter, sans-serif';
      ctx.fillText(`${Math.round(zone.disruption_probability * 100)}%`, x, y + 5);
    });

    // Title
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Bengaluru Risk Heatmap', 10, height - 10);

  }, [zones, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        borderRadius: 16,
        border: '1px solid rgba(255,255,255,0.06)',
        backgroundColor: 'rgba(0,0,0,0.2)',
      }}
    />
  );
}
