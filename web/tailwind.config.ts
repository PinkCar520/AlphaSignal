import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        // 金融语义色
        bullish: {
          DEFAULT: "#10b981", // Emerald 500
          glow: "rgba(16, 185, 129, 0.5)",
        },
        bearish: {
          DEFAULT: "#ef4444", // Red 500
          glow: "rgba(239, 68, 68, 0.5)",
        },
        gold: {
          DEFAULT: "#eab308", // Yellow 500
          glow: "rgba(234, 179, 8, 0.5)",
        },
        surface: {
          DEFAULT: "#0f172a", // Slate 900
          light: "#1e293b",   // Slate 800
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'grid-pattern': "linear-gradient(to right, #1e293b 1px, transparent 1px), linear-gradient(to bottom, #1e293b 1px, transparent 1px)",
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
};

export default config;
