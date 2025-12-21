import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'match-green': '#10b981',     // > 85% match
        'match-yellow': '#f59e0b',    // 60-84% match
        'match-red': '#ef4444',       // < 60% match
        'brand-primary': '#3b82f6',   // Corporate branding
        'brand-secondary': '#1e40af',
      },
      spacing: {
        '60': '60%',
        '40': '40%',
      },
    },
  },
  plugins: [],
};

export default config;

