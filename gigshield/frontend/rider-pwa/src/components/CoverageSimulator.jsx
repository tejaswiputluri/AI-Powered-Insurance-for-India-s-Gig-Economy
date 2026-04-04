/**
 * CoverageSimulator — Interactive slider-based coverage preview.
 * Inputs: Zone, disruption hours, signal count.
 * Output: Estimated payout with breakdown.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { simulateCoverage } from '../services/api';
import { formatRupees } from '../utils/formatters';

export default function CoverageSimulator({ defaultZone = 'BTM_LAYOUT' }) {
  const [zoneId, setZoneId] = useState(defaultZone);
  const [disruptionHours, setDisruptionHours] = useState(4);
  const [signalCount, setSignalCount] = useState(2);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulate = useCallback(async () => {
    setLoading(true);
    try {
      const response = await simulateCoverage({
        zone_id: zoneId,
        disruption_hours: disruptionHours,
        signal_count: signalCount,
      });
      setResult(response);
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setLoading(false);
    }
  }, [zoneId, disruptionHours, signalCount]);

  useEffect(() => {
    simulate();
  }, [simulate]);

  return (
    <div style={{
      backgroundColor: 'rgba(255,255,255,0.03)',
      borderRadius: 16, padding: 20,
    }}>
      <div style={{ fontSize: 14, fontWeight: 600, color: '#fff', marginBottom: 16 }}>
        🎮 Coverage Simulator
      </div>

      {/* Disruption Hours slider */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>Disruption Hours</span>
          <span style={{ fontSize: 14, fontWeight: 600, color: '#818cf8' }}>{disruptionHours}h</span>
        </div>
        <input
          type="range" min="1" max="8" step="1"
          value={disruptionHours}
          onChange={(e) => setDisruptionHours(Number(e.target.value))}
          style={{ width: '100%', accentColor: '#6366f1' }}
        />
      </div>

      {/* Signal Count */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 6 }}>
          Signals Confirmed
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {[2, 3].map(n => (
            <button
              key={n}
              onClick={() => setSignalCount(n)}
              style={{
                flex: 1, padding: '10px 16px', borderRadius: 10,
                backgroundColor: signalCount === n ? 'rgba(99,102,241,0.2)' : 'rgba(255,255,255,0.04)',
                border: `1px solid ${signalCount === n ? '#6366f1' : 'rgba(255,255,255,0.06)'}`,
                color: '#fff', cursor: 'pointer', fontSize: 13, fontWeight: 600,
              }}
            >
              {n} Signals {n === 3 ? '(High)' : '(Standard)'}
            </button>
          ))}
        </div>
      </div>

      {/* Result */}
      {result && (
        <div style={{
          backgroundColor: 'rgba(99,102,241,0.06)', borderRadius: 12,
          padding: 16, textAlign: 'center',
        }}>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', marginBottom: 4 }}>
            Estimated Payout
          </div>
          <div style={{ fontSize: 28, fontWeight: 700, color: '#22c55e' }}>
            {loading ? '...' : formatRupees(result.estimated_payout_paise)}
          </div>
          {result.breakdown && (
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginTop: 8 }}>
              {formatRupees(result.breakdown.baseline_hourly_paise)}/hr × {result.breakdown.disruption_hours}h
              × {result.breakdown.zone_impact_factor} ZIF
              × {result.breakdown.coverage_factor} CF
            </div>
          )}
        </div>
      )}
    </div>
  );
}
