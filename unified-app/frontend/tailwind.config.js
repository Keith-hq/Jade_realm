/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:     '#1a1a1a',
        card:   '#262626',
        border: '#333333',
        jade:   { DEFAULT: '#4ade80', deep: '#22c55e', dark: '#166534' },
        gold:   { DEFAULT: '#fbbf24', deep: '#f59e0b' },
        seal:   '#dc2626',
        fg:     { primary: '#f5f5f4', secondary: '#a8a29e', tertiary: '#57534e' },
      },
      fontFamily: {
        display: ['"Noto Serif SC"', 'serif'],
        calligraphy: ['"Ma Shan Zheng"', 'cursive'],
        body: ['"Noto Sans SC"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
