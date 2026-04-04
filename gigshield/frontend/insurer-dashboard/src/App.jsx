/**
 * GigShield Insurer Dashboard — Main App.
 * Desktop-first analytics dashboard with 5 pages.
 */

import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Overview from './pages/Overview';
import RiskHeatmap from './pages/RiskHeatmap';
import FraudQueue from './pages/FraudQueue';
import ClaimsViewer from './pages/ClaimsViewer';
import Reserves from './pages/Reserves';

const navItems = [
  { path: '/', label: 'Overview', icon: '📊' },
  { path: '/heatmap', label: 'Risk Map', icon: '🗺️' },
  { path: '/fraud', label: 'Fraud Queue', icon: '🔍' },
  { path: '/claims', label: 'Claims', icon: '📋' },
  { path: '/reserves', label: 'Reserves', icon: '💰' },
];

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex">
        {/* Sidebar */}
        <aside className="w-64 bg-[#080c1a] border-r border-white/5 p-6 flex flex-col">
          <div className="mb-8">
            <h1 className="text-xl font-bold">
              <span className="text-[#E89B0A]">⚡</span> GigShield
            </h1>
            <p className="text-white/30 text-xs mt-1">Insurer Dashboard</p>
          </div>

          <nav className="space-y-1 flex-1">
            {navItems.map(({ path, label, icon }) => (
              <NavLink
                key={path}
                to={path}
                end={path === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-colors ${
                    isActive
                      ? 'bg-[#E89B0A]/10 text-[#E89B0A] font-semibold'
                      : 'text-white/50 hover:text-white/80 hover:bg-white/5'
                  }`
                }
              >
                <span>{icon}</span>
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="mt-auto pt-4 border-t border-white/5">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[#E89B0A]/20 flex items-center justify-center text-sm">
                🏢
              </div>
              <div>
                <p className="text-sm font-medium">GigShield Insurer</p>
                <p className="text-xs text-white/30">Demo Mode</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-8 overflow-auto">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/heatmap" element={<RiskHeatmap />} />
            <Route path="/fraud" element={<FraudQueue />} />
            <Route path="/claims" element={<ClaimsViewer />} />
            <Route path="/reserves" element={<Reserves />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
