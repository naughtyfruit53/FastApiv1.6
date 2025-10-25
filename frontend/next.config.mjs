import path from "path";

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    reactCompiler: false,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://fastapiv16-production.up.railway.app",
    NEXT_PUBLIC_SNAPPYMAIL_URL: process.env.NEXT_PUBLIC_SNAPPYMAIL_URL || "http://localhost:8888",
  },
  transpilePackages: ["@mui/x-data-grid"],
  allowedDevOrigins: ["127.0.0.1", "localhost"],

  // Skip ESLint & TypeScript errors during build
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },

  webpack(config) {
    config.resolve.alias["@services"] = path.join(process.cwd(), "src/services");
    config.resolve.alias["@lib"] = path.join(process.cwd(), "src/lib");
    return config;
  },

  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://fastapiv16-production.up.railway.app";
    return [
      {
        source: '/api/customers',
        destination: `${apiUrl}/api/v1/customers`, // Explicitly map to /api/v1/customers
      },
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`, // General rewrite for other API routes
      },
    ];
  },
};

export default nextConfig;