/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./src/**/**/*.{js,jsx,ts,tsx}",
    "./src/components/**/*.{js,jsx,ts,tsx}",
    "./src/provider/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        light_primary: "#E8EBF7",
        light_secondary: "#ACBED8",
        light_action: "#DE1A1A",
        light_action_active: "#B71515",
        light_subheading: "#1F1F1F",
        dark_primary: "#1E1E24",
        dark_secondary: "#56718A",
        dark_action: "#ED2A1D",
        dark_action_active: "#BD1B0F",
        dark_subheading: "#E0E0E0",
      },
    },
  },
  plugins: [],
}

