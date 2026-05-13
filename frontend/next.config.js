/** @type {import('next').NextConfig} */
const nextConfig = {
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  experimental: {
    serverActions: {
      allowedOrigins: ["pukat-master:8100", "pukat-master:3000", "pukat-master", "100.85.142.33:8100", "100.85.142.33"]
    }
  },
  devIndicators: {
    appIsrStatus: true,
  },
};

module.exports = nextConfig;
