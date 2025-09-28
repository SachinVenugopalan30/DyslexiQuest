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
        'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
        'fade-in-up-delay-1': 'fadeInUp 0.8s ease-out 0.5s forwards',
        'fade-in-up-delay-2': 'fadeInUp 0.8s ease-out 1s forwards',
        'fade-in-up-delay-3': 'fadeInUp 0.8s ease-out 1.5s forwards',
        'glitch': 'glitch 2s infinite',
        'choice-button-enter': 'choiceButtonEnter 0.4s ease-out forwards',
        'story-content': 'storyContentEnter 0.6s ease-out forwards',
        'smooth-blink': 'smoothBlink 1.2s ease-in-out infinite',
        'smooth-fade-in': 'smoothFadeIn 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards',
        'smooth-fade-out': 'smoothFadeOut 0.4s cubic-bezier(0.55, 0.085, 0.68, 0.53) forwards',
        'component-enter': 'componentEnter 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards',
        'component-enter-delay-1': 'componentEnter 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) 0.2s forwards',
        'component-enter-delay-2': 'componentEnter 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) 0.4s forwards',
        'component-enter-delay-3': 'componentEnter 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) 0.6s forwards',
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
        },
        fadeInUp: {
          'to': { opacity: '1', transform: 'translateY(0)' }
        },
        glitch: {
          '0%, 100%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' }
        },
        choiceButtonEnter: {
          '0%': { opacity: '0', transform: 'translateY(20px) scale(0.95)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' }
        },
        storyContentEnter: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        smoothBlink: {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' }
        },
        smoothFadeIn: {
          '0%': { opacity: '0', transform: 'translateY(30px) scale(0.95)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' }
        },
        smoothFadeOut: {
          '0%': { opacity: '1', transform: 'translateY(0) scale(1)' },
          '100%': { opacity: '0', transform: 'translateY(-20px) scale(0.98)' }
        },
        componentEnter: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
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
