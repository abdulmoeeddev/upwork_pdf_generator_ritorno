/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#AD2831',
          dark: '#8D1F28'
        },
        background: {
          DEFAULT: '#121212',
          light: '#1E1E1E',
          lighter: '#2D2D2D'
        }
      }
    },
  },
  plugins: [],
}