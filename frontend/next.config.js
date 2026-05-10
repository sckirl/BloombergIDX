/** @type {import('next').NextConfig} */
const nextConfig = {
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  experimental: {
    serverActions: {
      allowedOrigins: ["pukat-master:6969", "pukat-master:3000", "pukat-master", "100.85.142.33:6969", "100.85.142.33"]
    }
  },
  devIndicators: {
    appIsrStatus: true,
  },
};

module.exports = nextConfig;
