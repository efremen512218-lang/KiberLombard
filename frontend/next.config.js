/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['steamcdn-a.akamaihd.net', 'community.cloudflare.steamstatic.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
