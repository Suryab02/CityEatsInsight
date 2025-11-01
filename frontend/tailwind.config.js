/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        text: {
          primary: 'rgb(var(--text-primary) / <alpha-value>)',
          secondary: 'rgb(var(--text-secondary) / <alpha-value>)',
          muted: 'rgb(var(--text-muted) / <alpha-value>)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    function ({ addUtilities }) {
      addUtilities({
        '.text-title': {
          '@apply text-3xl font-bold text-text-primary': {},
        },
        '.text-subtitle': {
          '@apply text-xl font-semibold text-text-secondary': {},
        },
        '.text-body': {
          '@apply text-base text-text-secondary leading-relaxed': {},
        },
        '.text-muted': {
          '@apply text-sm text-text-muted': {},
        },
      });
    },
  ],
};
