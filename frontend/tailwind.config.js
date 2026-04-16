/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0F1117',
        surface: '#1A1D27',
        'surface-raised': '#22263A',
        border: '#2E3248',
        primary: {
          DEFAULT: '#6C63FF',
          hover: '#5A52E0',
        },
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
        text: {
          primary: '#F1F5F9',
          secondary: '#94A3B8',
          muted: '#475569',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      fontSize: {
        xs: '11px',
        sm: '13px',
        base: '15px',
        md: '17px',
        lg: '22px',
        xl: '30px',
      },
      spacing: {
        1: '4px',
        2: '8px',
        3: '12px',
        4: '16px',
        5: '20px',
        6: '24px',
        8: '32px',
        10: '40px',
        12: '48px',
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '16px',
        full: '9999px',
      },
      boxShadow: {
        card: '0 2px 12px rgba(0,0,0,0.35)',
        modal: '0 8px 40px rgba(0,0,0,0.6)',
        dropdown: '0 4px 20px rgba(0,0,0,0.4)',
      },
    },
  },
  plugins: [],
}
