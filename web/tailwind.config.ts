import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      boxShadow: {
        panel: "0 24px 80px rgba(7, 12, 20, 0.28)",
      },
      colors: {
        ink: "#081120",
        mist: "#dce4ec",
        signal: "#7bf1a8",
        ember: "#ff8c69",
        alert: "#ff5d73",
        cobalt: "#59b2ff",
      },
      backgroundImage: {
        "hero-grid":
          "linear-gradient(rgba(123, 241, 168, 0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(123, 241, 168, 0.08) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;
