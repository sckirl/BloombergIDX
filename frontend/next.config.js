/** @type {import('next').NextConfig} */
const nextConfig = {
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  async rewrites() {
    const target = process.env.NEXT_PUBLIC_API_URL || 'https://oecd-minority-intense-dark.trycloudflare.com';
    return [
      {
        source: '/insider/:path*',
        destination: `${target}/insider/:path*`,
      },
    ];
  },
  experimental: {
    serverActions: {
      allowedOrigins: ["*"]
    }
  },
  devIndicators: {
    appIsrStatus: true,
  },
};

module.exports = nextConfig;
