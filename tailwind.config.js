/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/*.html",
    "./templates/**/*.html",
    "./templates/partials/*.html",
    "./src/templates/**/*.html",
  ],
  theme: {
    darkMode: false,
    extend: {},
  },
  plugins: [require("daisyui")],
};
