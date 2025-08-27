/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    reactCompiler: true,
  },
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000",
    NEXT_PUBLIC_ENABLE_PASSWORD_CHANGE:
      process.env.NEXT_PUBLIC_ENABLE_PASSWORD_CHANGE || "true",
  },
  transpilePackages: ['@mui/x-data-grid'], // Add this to handle CSS from MUI X DataGrid
  allowedDevOrigins: ["127.0.0.1", "localhost"], // Add this to fix the cross-origin warning
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${
          process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
        }/api/:path*`,
      },
    ];
  },
};

export default nextConfig;