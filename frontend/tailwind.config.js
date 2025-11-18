/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tbank: {
          yellow: '#FFDD2D',
          'yellow-dark': '#FFD700',
          black: '#1F1F1F',
          'black-light': '#2A2A2A',
          gray: '#9E9E9E',
          'gray-light': '#E0E0E0',
          'gray-dark': '#424242',
        },
      },
      fontFamily: {
        sans: ['TinkoffSans', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'tbank': '0 4px 16px rgba(255, 221, 45, 0.1)',
        'tbank-lg': '0 8px 32px rgba(255, 221, 45, 0.15)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}

