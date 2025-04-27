/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    // 确保支持流式输出的Edge Functions
    serverActions: true,
  }
}

module.exports = nextConfig 