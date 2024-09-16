/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html",
        "./templates/partials/*.html",
    ],
    theme: {
        extend: {},
    },
    plugins: [require("daisyui")],
}

