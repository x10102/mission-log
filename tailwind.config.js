/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.j2"],
  theme: {
    extend: {
      boxShadow: {
        'glow': 'rgba(255, 255, 255, 0.2) 0px 2px 8px 0px;',
      }
    },
  },
  plugins: [],
}

