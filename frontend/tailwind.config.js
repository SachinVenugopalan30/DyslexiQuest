/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Poppins', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Arial', 'sans-serif'],
        'poppins': ['Poppins', 'system-ui', 'sans-serif'],
        'dyslexic': ['OpenDyslexic', 'Poppins', 'sans-serif'],
        'mono': ['SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Consolas', 'monospace'],
        'accessible': ['Atkinson Hyperlegible', 'Poppins', 'sans-serif'],
      },
      colors: {
        // New color scheme from the image
        'primary': {
          'green': '#5A7D7C',      // Hooker's green
          'lavender': '#DADFF7',    // Lavender web
          'gunmetal': '#232C33',    // Gunmetal
          'powder': '#A0C1D1',      // Powder blue
          'gray': '#B5B2C2',        // French gray
        },
        // Legacy retro theme (for backward compatibility)
        'retro': {
          'black': '#232C33',       // Updated to use gunmetal instead of pure black
          'green': '#5A7D7C',       // Updated to use hooker's green
          'amber': '#A0C1D1',       // Updated to use powder blue
          'dark-green': '#5A7D7C',  // Same as primary green
        },
        'accessible': {
          'bg': '#232C33',          // Gunmetal for better contrast
          'text': '#DADFF7',        // Lavender for readability
          'accent': '#A0C1D1',      // Powder blue
          'secondary': '#B5B2C2',   // French gray
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
