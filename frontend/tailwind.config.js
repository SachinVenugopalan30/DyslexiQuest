/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'mono': ['SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Consolas', 'monospace'],
        'dyslexic': ['OpenDyslexic', 'Atkinson Hyperlegible', 'sans-serif'],
        'accessible': ['Atkinson Hyperlegible', 'OpenDyslexic', 'sans-serif'],
      },
      colors: {
        'retro': {
          'black': '#000000',
          'green': '#00ff00',
          'amber': '#ffb000',
          'dark-green': '#008000',
        },
        'accessible': {
          'bg': '#1a1a1a',
          'text': '#ffffff',
          'accent': '#4a9eff',
          'secondary': '#ffd700',
        }
      },
      animation: {
        'typewriter': 'typewriter 2s steps(40, end)',
        'blink': 'blink 1s step-end infinite',
        'fade-in': 'fadeIn 0.3s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        typewriter: {
          'from': { width: '0' },
          'to': { width: '100%' }
        },
        blink: {
          '50%': { opacity: '0' }
        },
        fadeIn: {
          'from': { opacity: '0' },
          'to': { opacity: '1' }
        },
        slideUp: {
          'from': { transform: 'translateY(20px)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' }
        }
      },
      screens: {
        'tablet': '768px',
        'laptop': '1024px',
        'desktop': '1280px',
      },
    },
  },
  plugins: [],
}
