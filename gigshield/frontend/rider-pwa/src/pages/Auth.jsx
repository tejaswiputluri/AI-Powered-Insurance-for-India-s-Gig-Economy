/**
 * Auth Page — Login/Signup with Phone OTP and Facebook.
 * First screen users see before onboarding.
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { loginWithPhone, loginWithFacebook, demoLogin } from '../services/api';
import { FaFacebook, FaPhone, FaPlay } from 'react-icons/fa';

const IS_DEMO = import.meta.env.VITE_DEMO_MODE !== 'false';

export default function Auth() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [showOtp, setShowOtp] = useState(false);
  const [otpSent, setOtpSent] = useState(false);

  const handlePhoneLogin = async () => {
    if (!phoneNumber || phoneNumber.length < 10) {
      toast.error('Please enter a valid phone number');
      return;
    }

    setLoading(true);
    try {
      if (!otpSent) {
        // Send OTP
        await loginWithPhone(phoneNumber);
        setOtpSent(true);
        setShowOtp(true);
        toast.success('OTP sent to your phone!');
      } else {
        // Verify OTP
        if (!otp || otp.length < 4) {
          toast.error('Please enter the 4-digit OTP');
          return;
        }

        const response = await loginWithPhone(phoneNumber, otp);
        localStorage.setItem('gigshield_token', response.access_token);
        localStorage.setItem('gigshield_rider_id', response.rider_id);

        toast.success('Login successful!');
        navigate('/onboarding');
      }
    } catch (error) {
      console.error('Phone login error:', error);
      toast.error(error.response?.data?.detail?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleFacebookLogin = async () => {
    setLoading(true);
    try {
      const response = await loginWithFacebook();
      localStorage.setItem('gigshield_token', response.access_token);
      localStorage.setItem('gigshield_rider_id', response.rider_id);

      toast.success('Facebook login successful!');
      navigate('/onboarding');
    } catch (error) {
      console.error('Facebook login error:', error);
      toast.error('Facebook login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setLoading(true);
    try {
      const response = await demoLogin();
      localStorage.setItem('gigshield_token', response.access_token);
      localStorage.setItem('gigshield_rider_id', response.rider_id);

      toast.success('Demo login successful!');
      navigate('/onboarding');
    } catch (error) {
      console.error('Demo login error:', error);
      toast.error('Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-500 via-navy-600 to-navy-700 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
            className="text-6xl mb-4"
          >
            ⚡
          </motion.div>
          <h1 className="text-3xl font-bold gold-gradient mb-2">GigShield</h1>
          <p className="text-white/70">Insurance for India's Gig Workers</p>
        </div>

        {/* Auth Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
        >
          <h2 className="text-xl font-semibold text-white mb-6 text-center">
            Welcome Back
          </h2>

          {/* Phone Login */}
          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Phone Number
              </label>
              <div className="relative">
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ''))}
                  placeholder="Enter your phone number"
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-gold-400"
                  maxLength={10}
                />
                <FaPhone className="absolute right-3 top-3.5 text-white/50" />
              </div>
            </div>

            {showOtp && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
              >
                <label className="block text-sm font-medium text-white/80 mb-2">
                  Enter OTP
                </label>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                  placeholder="0000"
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-gold-400 text-center text-xl tracking-widest"
                  maxLength={4}
                />
              </motion.div>
            )}

            <button
              onClick={handlePhoneLogin}
              disabled={loading}
              className="w-full bg-gold-500 hover:bg-gold-600 disabled:bg-gold-300 text-navy-900 font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-navy-900 border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <FaPhone />
                  {otpSent ? 'Verify OTP' : 'Send OTP'}
                </>
              )}
            </button>
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/20" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-transparent text-white/60">or</span>
            </div>
          </div>

          {/* Facebook Login */}
          <button
            onClick={handleFacebookLogin}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 mb-4"
          >
            <FaFacebook />
            Continue with Facebook
          </button>

          {/* Demo Login */}
          {IS_DEMO && (
            <button
              onClick={handleDemoLogin}
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <FaPlay />
              Try Demo
            </button>
          )}
        </motion.div>

        {/* Footer */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-white/50 text-sm mt-6"
        >
          By continuing, you agree to our Terms of Service and Privacy Policy
        </motion.p>
      </motion.div>
    </div>
  );
}