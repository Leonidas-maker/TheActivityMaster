/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,jsx,ts,tsx}",
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

        light_event: "#8344C2",
        light_event_active: "#7037A9",

        dark_event: "#66329A",
        dark_event_active: "#52287B",

        //* Course cancelled
        light_course_cancelled: "#8b0000",
        light_course_cancelled_active: "#b22727",
        dark_cancelled_course: "#640b0b",
        dark_cancelled_course_active: "#832a2a",

        //* Course
        light_course: "#006400",
        light_course_active: "#1c811c",
        dark_course: "#084808",
        dark_course_active: "#1f5f1f",

        //* Course rescheduled
        

      },
    },
  },
  plugins: [],
}

