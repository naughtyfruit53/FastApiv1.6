import path from "path";

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    reactCompiler: false,
  },
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000",
    NEXT_PUBLIC_ENABLE_PASSWORD_CHANGE:
      process.env.NEXT_PUBLIC_ENABLE_PASSWORD_CHANGE || "true",
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
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    return [
      {
        source: "/api/customers",
        destination: `${apiUrl}/api/v1/customers`, // Explicitly map to /api/v1/customers
      },
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`, // General rewrite for other API routes
      },
    ];
  },
};

export default nextConfig;