/**
 * Onboarding Page — 5-step PRF data collection.
 * Full screen, one question per screen, progress bar.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { onboardRider } from '../services/api';
import toast from 'react-hot-toast';

const ZONES = [
  { id: 'BTM_LAYOUT', name: 'BTM Layout' },
  { id: 'KORAMANGALA', name: 'Koramangala' },
  { id: 'INDIRANAGAR', name: 'Indiranagar' },
  { id: 'WHITEFIELD', name: 'Whitefield' },
  { id: 'JAYANAGAR', name: 'Jayanagar' },
  { id: 'MARATHAHALLI', name: 'Marathahalli' },
  { id: 'HSR_LAYOUT', name: 'HSR Layout' },
  { id: 'ELECTRONIC_CITY', name: 'Electronic City' },
  { id: 'HEBBAL', name: 'Hebbal' },
  { id: 'JP_NAGAR', name: 'JP Nagar' },
];

const EARNING_PRESETS = [
  { value: 400, label: '< ₹500/day' },
  { value: 650, label: '₹500–800/day' },
  { value: 1000, label: '₹800–1,200/day' },
  { value: 1400, label: '₹1,200–1,600/day' },
  { value: 1800, label: '> ₹1,600/day' },
];

export default function Onboarding({ onComplete }) {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: '',
    zone_id: '',
    platform: '',
    work_hours_start: 10,
    work_hours_end: 22,
    work_days_per_week: 6,
    self_reported_daily_earning: 1000,
  });

  const totalSteps = 5;

  const handleSubmit = async () => {
    setLoading(true);
    try {
      console.log('Submitting form:', form);
      const res = await onboardRider(form);
      console.log('Onboard response:', res);
      onComplete?.(res);
      toast.success('Profile created! 🎉');
      navigate('/premium');
    } catch (err) {
      console.error('Onboarding error:', err);
      const errMsg = 
        err.response?.data?.error?.message || 
        err.response?.data?.detail?.message || 
        err.response?.data?.detail || 
        err.message || 
        'Failed to onboard';
      toast.error(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const canProceed = () => {
    switch (step) {
      case 1: return form.name.length >= 2;
      case 2: return form.zone_id !== '';
      case 3: return form.platform !== '';
      case 4: return form.work_hours_end > form.work_hours_start;
      case 5: return form.self_reported_daily_earning > 0;
      default: return false;
    }
  };

  const slideVariants = {
    enter: { x: 100, opacity: 0 },
    center: { x: 0, opacity: 1 },
    exit: { x: -100, opacity: 0 },
  };

  return (
    <div className="min-h-screen bg-navy-500 flex flex-col">
      {/* Progress bar */}
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-white/60 text-sm font-medium">{step} of {totalSteps}</span>
          <span className="text-gold-500 text-sm font-semibold">⚡ GigShield</span>
        </div>
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-gold-500 to-gold-300 rounded-full"
            animate={{ width: `${(step / totalSteps) * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col justify-center px-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.25 }}
          >
            {step === 1 && (
              <div>
                <h2 className="text-3xl font-bold mb-2">What's your name?</h2>
                <p className="text-white/50 mb-8">We'll personalise your coverage</p>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="Enter your name"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-4 text-lg text-white placeholder-white/30 focus:outline-none focus:border-gold-500 transition-colors"
                  autoFocus
                />
              </div>
            )}

            {step === 2 && (
              <div>
                <h2 className="text-3xl font-bold mb-2">Your delivery zone</h2>
                <p className="text-white/50 mb-6">Where do you mostly deliver?</p>
                <div className="grid grid-cols-2 gap-3">
                  {ZONES.map((zone) => (
                    <button
                      key={zone.id}
                      onClick={() => setForm({ ...form, zone_id: zone.id })}
                      className={`p-4 rounded-xl text-left transition-all ${
                        form.zone_id === zone.id
                          ? 'bg-gold-500/20 border-2 border-gold-500 text-gold-500'
                          : 'bg-white/5 border-2 border-transparent text-white/70 hover:bg-white/10'
                      }`}
                    >
                      <span className="font-medium">{zone.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {step === 3 && (
              <div>
                <h2 className="text-3xl font-bold mb-2">Your platform</h2>
                <p className="text-white/50 mb-8">Which platform do you deliver for?</p>
                <div className="space-y-3">
                  {['swiggy', 'zomato', 'dunzo'].map((p) => (
                    <button
                      key={p}
                      onClick={() => setForm({ ...form, platform: p })}
                      className={`w-full p-5 rounded-xl text-left text-lg transition-all flex items-center gap-4 ${
                        form.platform === p
                          ? 'bg-gold-500/20 border-2 border-gold-500'
                          : 'bg-white/5 border-2 border-transparent hover:bg-white/10'
                      }`}
                    >
                      <span className="text-2xl">
                        {p === 'swiggy' ? '🟠' : p === 'zomato' ? '🔴' : '🟢'}
                      </span>
                      <span className="font-semibold capitalize">{p}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {step === 4 && (
              <div>
                <h2 className="text-3xl font-bold mb-2">Work schedule</h2>
                <p className="text-white/50 mb-8">When do you usually work?</p>

                <div className="space-y-6">
                  <div>
                    <label className="text-white/60 text-sm block mb-2">Start Time</label>
                    <select
                      value={form.work_hours_start}
                      onChange={(e) => setForm({ ...form, work_hours_start: parseInt(e.target.value) })}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-gold-500"
                    >
                      {Array.from({ length: 24 }, (_, i) => (
                        <option key={i} value={i} className="bg-navy-700">
                          {i.toString().padStart(2, '0')}:00
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-white/60 text-sm block mb-2">End Time</label>
                    <select
                      value={form.work_hours_end}
                      onChange={(e) => setForm({ ...form, work_hours_end: parseInt(e.target.value) })}
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-gold-500"
                    >
                      {Array.from({ length: 24 }, (_, i) => (
                        <option key={i} value={i} className="bg-navy-700">
                          {i.toString().padStart(2, '0')}:00
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-white/60 text-sm block mb-2">
                      Days per week: <span className="text-gold-500 font-bold">{form.work_days_per_week}</span>
                    </label>
                    <input
                      type="range"
                      min="1" max="7"
                      value={form.work_days_per_week}
                      onChange={(e) => setForm({ ...form, work_days_per_week: parseInt(e.target.value) })}
                      className="w-full accent-gold-500"
                    />
                    <div className="flex justify-between text-xs text-white/30 mt-1">
                      <span>1</span><span>7</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {step === 5 && (
              <div>
                <h2 className="text-3xl font-bold mb-2">Daily earnings</h2>
                <p className="text-white/50 mb-8">Roughly how much do you earn per day?</p>
                <div className="space-y-3">
                  {EARNING_PRESETS.map((preset) => (
                    <button
                      key={preset.value}
                      onClick={() => setForm({ ...form, self_reported_daily_earning: preset.value })}
                      className={`w-full p-4 rounded-xl text-left transition-all ${
                        form.self_reported_daily_earning === preset.value
                          ? 'bg-gold-500/20 border-2 border-gold-500'
                          : 'bg-white/5 border-2 border-transparent hover:bg-white/10'
                      }`}
                    >
                      <span className="font-medium text-lg">{preset.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation buttons */}
      <div className="p-6 space-y-3">
        {step < totalSteps ? (
          <button
            onClick={() => setStep(step + 1)}
            disabled={!canProceed()}
            className="w-full bg-gold-500 text-navy-500 py-4 rounded-xl font-bold text-lg disabled:opacity-30 disabled:cursor-not-allowed hover:bg-gold-400 transition-colors"
          >
            Continue →
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={loading || !canProceed()}
            className="w-full bg-gold-500 text-navy-500 py-4 rounded-xl font-bold text-lg disabled:opacity-30 hover:bg-gold-400 transition-colors"
          >
            {loading ? 'Setting up...' : 'Get My Premium ⚡'}
          </button>
        )}

        {step > 1 && (
          <button
            onClick={() => setStep(step - 1)}
            className="w-full text-white/40 py-2 text-sm hover:text-white/60 transition-colors"
          >
            ← Back
          </button>
        )}
      </div>
    </div>
  );
}
