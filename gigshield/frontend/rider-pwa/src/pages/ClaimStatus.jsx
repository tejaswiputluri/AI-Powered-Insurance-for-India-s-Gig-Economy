/**
 * ClaimStatus — live view of a claim with confidence gauge.
 * Auto-refreshes every 10 seconds.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getClaimDetail, getClaimTimeline } from '../services/api';
import { formatRupees, formatIST, getStatusDisplay } from '../utils/formatters';

export default function ClaimStatus() {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadClaim();
    const interval = setInterval(loadClaim, 10000);
    return () => clearInterval(interval);
  }, [claimId]);

  async function loadClaim() {
    try {
      const [claimRes, timelineRes] = await Promise.all([
        getClaimDetail(claimId),
        getClaimTimeline(claimId),
      ]);
      setClaim(claimRes?.data);
      setTimeline(timelineRes?.events || []);
    } catch (err) {
      console.error('Failed to load claim:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading || !claim) {
    return (
      <div className="min-h-screen bg-navy-500 flex items-center justify-center">
        <p className="text-white/50">Loading claim...</p>
      </div>
    );
  }

  const status = getStatusDisplay(claim.status);
  const score = claim.confidence_score || 0;

  return (
    <div className="min-h-screen bg-navy-500 px-6 py-8">
      {/* Header */}
      <button onClick={() => navigate(-1)} className="text-white/40 text-sm mb-6 hover:text-white/60">
        ← Back
      </button>

      {/* Status */}
      <div className="text-center mb-8">
        <span className={`inline-block px-4 py-2 rounded-full text-sm font-bold ${status.bg} ${status.color}`}>
          {status.label}
        </span>
      </div>

      {/* Confidence Gauge */}
      <motion.div
        className="glass-card p-6 mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <p className="text-center text-white/40 text-sm mb-4">Confidence Score</p>

        {/* SVG Semicircle Gauge */}
        <div className="relative w-48 h-28 mx-auto mb-4">
          <svg viewBox="0 0 200 110" className="w-full h-full">
            {/* Background arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="12"
              strokeLinecap="round"
            />
            {/* Score segments */}
            {/* Red: 0-34 */}
            <path d="M 20 100 A 80 80 0 0 1 54.5 35.5" fill="none" stroke="#C0392B" strokeWidth="12" strokeLinecap="round" opacity="0.4" />
            {/* Orange: 35-59 */}
            <path d="M 54.5 35.5 A 80 80 0 0 1 100 20" fill="none" stroke="#E67E22" strokeWidth="12" strokeLinecap="round" opacity="0.4" />
            {/* Yellow: 60-84 */}
            <path d="M 100 20 A 80 80 0 0 1 145.5 35.5" fill="none" stroke="#F39C12" strokeWidth="12" strokeLinecap="round" opacity="0.4" />
            {/* Green: 85-100 */}
            <path d="M 145.5 35.5 A 80 80 0 0 1 180 100" fill="none" stroke="#1A7A35" strokeWidth="12" strokeLinecap="round" opacity="0.4" />

            {/* Needle */}
            <motion.line
              x1="100" y1="100"
              x2="100" y2="30"
              stroke="#E89B0A"
              strokeWidth="3"
              strokeLinecap="round"
              style={{ transformOrigin: '100px 100px' }}
              initial={{ rotate: -90 }}
              animate={{ rotate: -90 + (score / 100) * 180 }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            />
            <circle cx="100" cy="100" r="6" fill="#E89B0A" />
          </svg>

          {/* Score number */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center">
            <motion.p
              className="text-3xl font-extrabold gold-gradient"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              {score}
            </motion.p>
            <p className="text-white/30 text-xs">out of 100</p>
          </div>
        </div>

        {/* Segment labels */}
        <div className="flex justify-between text-xs px-2">
          <span className="text-red-400">Reject</span>
          <span className="text-orange-400">Review</span>
          <span className="text-yellow-400">Flag</span>
          <span className="text-green-400">Approve</span>
        </div>
      </motion.div>

      {/* Payout */}
      <motion.div
        className="glass-card p-6 mb-6 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <p className="text-white/40 text-sm mb-1">Payout Amount</p>
        <p className="text-4xl font-extrabold gold-gradient">
          {formatRupees(claim.capped_payout_paise)}
        </p>
        {claim.payout?.upi_vpa && (
          <p className="text-white/30 text-sm mt-2">→ {claim.payout.upi_vpa}</p>
        )}
      </motion.div>

      {/* Timeline */}
      {timeline.length > 0 && (
        <div className="mb-6">
          <p className="text-white/40 text-xs uppercase tracking-wider mb-4">Claim Timeline</p>
          <div className="space-y-0 relative">
            <div className="absolute left-3 top-3 bottom-3 w-0.5 bg-white/10" />
            {timeline.map((event, i) => (
              <motion.div
                key={i}
                className="flex items-start gap-4 pb-4"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.05 }}
              >
                <div className="w-6 h-6 rounded-full bg-gold-500/20 border-2 border-gold-500 flex items-center justify-center z-10 flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-gold-500" />
                </div>
                <div>
                  <p className="text-sm font-medium capitalize">
                    {event.event.replace(/_/g, ' ')}
                  </p>
                  <p className="text-white/40 text-xs">{event.detail}</p>
                  <p className="text-white/20 text-xs mt-0.5">{formatIST(event.timestamp)}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
