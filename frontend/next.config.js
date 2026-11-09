/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.amazon.**',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '**.jumia.**',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '**.aliexpress.**',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '**..alibaba.**',
        pathname: '/**',
      },
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig