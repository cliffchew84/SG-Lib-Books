/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/*.html",
        "./templates/**/*.html",
        "./templates/partials/*.html",
        "./src/templates/**/*.html",
    ],
    theme: {
        extend: {},
    },
    plugins: [require("daisyui")],
}

