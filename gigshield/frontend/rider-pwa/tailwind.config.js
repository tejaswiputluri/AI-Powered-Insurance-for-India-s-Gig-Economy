/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#e6f0f5',
          100: '#b3d1e0',
          200: '#80b3cc',
          300: '#4d94b8',
          400: '#1a76a3',
          500: '#002E4E',
          600: '#002944',
          700: '#00233b',
          800: '#001d31',
          900: '#001728',
        },
        gold: {
          50: '#fdf6e3',
          100: '#f9e8b3',
          200: '#f5da84',
          300: '#f1cc55',
          400: '#edbe25',
          500: '#E89B0A',
          600: '#c98508',
          700: '#a96f07',
          800: '#895a05',
          900: '#694404',
        },
        status: {
          success: '#1A7A35',
          warning: '#F39C12',
          danger: '#C0392B',
          info: '#2E86C1',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      animation: {
        'gauge-fill': 'gaugeFill 800ms ease-out forwards',
        'bar-grow': 'barGrow 600ms ease-out forwards',
        'fade-up': 'fadeUp 400ms ease-out forwards',
        'slide-in': 'slideIn 300ms ease-out forwards',
        'pulse-gold': 'pulseGold 2s ease-in-out infinite',
      },
      keyframes: {
        gaugeFill: {
          '0%': { transform: 'rotate(-90deg)' },
          '100%': { transform: 'rotate(var(--gauge-rotation))' },
        },
        barGrow: {
          '0%': { width: '0%' },
          '100%': { width: 'var(--bar-width)' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulseGold: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(232, 155, 10, 0.4)' },
          '50%': { boxShadow: '0 0 0 12px rgba(232, 155, 10, 0)' },
        },
      },
    },
  },
  plugins: [],
};
