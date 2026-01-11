import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Optimize for production
  reactStrictMode: true,

  // Image optimization
  images: {
    domains: [], // Add any external image domains if needed
    unoptimized: false,
  },

  // Environment variables validation
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
  },
};

export default nextConfig;
