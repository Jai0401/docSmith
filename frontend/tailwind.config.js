/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            color: '#fff',
            a: {
              color: '#3b82f6',
              '&:hover': {
                color: '#60a5fa',
              },
            },
            h1: {
              color: '#fff',
            },
            h2: {
              color: '#fff',
            },
            h3: {
              color: '#fff',
            },
            strong: {
              color: '#fff',
            },
            code: {
              color: '#fff',
              background: '#1f2937',
              padding: '0.2em 0.4em',
              borderRadius: '0.25rem',
            },
            pre: {
              background: '#1f2937',
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}

