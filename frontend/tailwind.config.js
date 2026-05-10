/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#000000",
        fg: "#D1D1D1",
        acc: "#FFA500", // Bloomberg Orange
        acc2: "#00E676", // Green
        acc3: "#FF1744", // Red
        acc4: "#2979FF", // Blue
        surface: "#121212",
        "border-custom": "#333333",
      },
    },
  },
  plugins: [],
};
