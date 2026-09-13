/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mars: {
          darkest: "#04070c",
          dark: "#080d16",
          panel: "#0e1624",
          surface: "#142033",
          border: "#1e2e47",
          borderBright: "#2d4468",
          rust: "#d95338",
          amber: "#e07a5f",
          sand: "#f4a261",
          gold: "#e9c46a",
          cyan: "#38bdf8",
          teal: "#2dd4bf",
          emerald: "#34d399",
          danger: "#ef4444",
          warning: "#f59e0b",
          info: "#0ea5e9"
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'panel': '0 4px 20px -2px rgba(0, 0, 0, 0.5)',
        'glow-cyan': '0 0 15px -3px rgba(56, 189, 248, 0.25)',
        'glow-amber': '0 0 15px -3px rgba(224, 122, 95, 0.25)',
      }
    },
  },
  plugins: [],
}
