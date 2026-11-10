/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Poppins", "system-ui", "sans-serif"],
      },
      colors: {
        brand: {
          50: "#EEF6EE",
          100: "#DCEDDC",
          200: "#B9DBB9",
          300: "#8FC48F",
          400: "#66AC66",
          500: "#4C8C4C",
          600: "#3B703D", // verde principal (logo, botones, nav activo)
          700: "#2F5A32",
          800: "#254527",
          900: "#1A311C",
        },
        canvas: "#F6F6FB", // fondo general de la app
        surface: "#FFFFFF", // fondo de tarjetas
        ink: "#1E2422", // texto principal
        muted: "#6B7280", // texto secundario
        line: "#E7E7F0", // bordes sutiles
      },
      boxShadow: {
        card: "0 1px 2px rgba(20, 20, 40, 0.04), 0 1px 10px rgba(20, 20, 40, 0.04)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [],
}
