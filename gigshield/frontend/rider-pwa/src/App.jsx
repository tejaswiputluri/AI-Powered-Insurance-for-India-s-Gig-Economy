/**
 * GigShield Rider PWA — Main App with routing.
 * Mobile-first PWA for delivery partners.
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Onboarding from './pages/Onboarding';
import PremiumPanel from './pages/PremiumPanel';
import Simulator from './pages/Simulator';
import PolicySelect from './pages/PolicySelect';
import Dashboard from './pages/Dashboard';
import ClaimStatus from './pages/ClaimStatus';
import ClaimHistory from './pages/ClaimHistory';
import { demoLogin } from './services/api';

const IS_DEMO = import.meta.env.VITE_DEMO_MODE !== 'false';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);
  const [riderData, setRiderData] = useState(null);
  const [premiumData, setPremiumData] = useState(null);

  useEffect(() => {
    initAuth();
  }, []);

  async function initAuth() {
    const token = localStorage.getItem('gigshield_token');
    if (token) {
      setIsLoggedIn(true);
      setLoading(false);
      return;
    }

    if (IS_DEMO) {
      try {
        const res = await demoLogin();
        localStorage.setItem('gigshield_token', res.access_token);
        localStorage.setItem('gigshield_rider_id', res.rider_id);
        setIsLoggedIn(true);
      } catch (err) {
        console.error('Demo login failed:', err);
      }
    }
    setLoading(false);
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-navy-500">
        <div className="text-center">
          <div className="text-4xl mb-4">⚡</div>
          <h1 className="text-2xl font-bold gold-gradient">GigShield</h1>
          <p className="text-white/50 mt-2">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      {IS_DEMO && <div className="demo-banner">⚡ DEMO MODE ⚡</div>}
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: '#002944',
            color: '#fff',
            border: '1px solid rgba(232, 155, 10, 0.3)',
          },
        }}
      />
      <Routes>
        <Route
          path="/"
          element={
            isLoggedIn ? <Navigate to="/dashboard" /> : <Navigate to="/onboarding" />
          }
        />
        <Route
          path="/onboarding"
          element={
            <Onboarding
              onComplete={(data) => {
                setPremiumData(data);
                setRiderData(data);
              }}
            />
          }
        />
        <Route
          path="/premium"
          element={<PremiumPanel premiumData={premiumData} />}
        />
        <Route path="/simulator" element={<Simulator />} />
        <Route
          path="/select-policy"
          element={
            <PolicySelect
              premiumData={premiumData}
              onPolicyCreated={() => setIsLoggedIn(true)}
            />
          }
        />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/claim/:claimId" element={<ClaimStatus />} />
        <Route path="/claims" element={<ClaimHistory />} />
      </Routes>
    </BrowserRouter>
  );
}
