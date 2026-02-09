/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for optimized Docker builds
  output: 'standalone',

  // Disable telemetry in production
  telemetry: {
    enabled: false,
  },
}

module.exports = nextConfig
