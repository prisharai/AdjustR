/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'adjustr-green': {
          light: '#8BA888',
          DEFAULT: '#6B8E7F',
          dark: '#4A6B5E',
        },
      },
    },
  },
  plugins: [],
}
