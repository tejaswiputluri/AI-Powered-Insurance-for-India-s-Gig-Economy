/**
 * GigShield Rider PWA — Main App with routing.
 * Mobile-first PWA for delivery partners.
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Auth from './pages/Auth';
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
            isLoggedIn ? <Navigate to="/dashboard" /> : <Navigate to="/auth" />
          }
        />
        <Route path="/auth" element={<Auth />} />
        <Route
          path="/onboarding"
          element={
            isLoggedIn ? (
              <Onboarding
                onComplete={(data) => {
                  setPremiumData(data);
                  setRiderData(data);
                }}
              />
            ) : (
              <Navigate to="/auth" />
            )
          }
        />
        <Route
          path="/premium"
          element={
            isLoggedIn ? (
              <PremiumPanel premiumData={premiumData} />
            ) : (
              <Navigate to="/auth" />
            )
          }
        />
        <Route
          path="/simulator"
          element={isLoggedIn ? <Simulator /> : <Navigate to="/auth" />}
        />
        <Route
          path="/select-policy"
          element={
            isLoggedIn ? (
              <PolicySelect
                premiumData={premiumData}
                onPolicyCreated={() => setIsLoggedIn(true)}
              />
            ) : (
              <Navigate to="/auth" />
            )
          }
        />
        <Route
          path="/dashboard"
          element={isLoggedIn ? <Dashboard /> : <Navigate to="/auth" />}
        />
        <Route
          path="/claim/:claimId"
          element={isLoggedIn ? <ClaimStatus /> : <Navigate to="/auth" />}
        />
        <Route
          path="/claims"
          element={isLoggedIn ? <ClaimHistory /> : <Navigate to="/auth" />}
        />
      </Routes>
    </BrowserRouter>
  );
}
