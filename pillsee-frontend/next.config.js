/** @type {import('next').NextConfig} */
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development'
});

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone', // Pro Docker produkci
  experimental: {
    optimizeCss: true,
  },
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif']
  },
  // API proxy pro development a Docker
  async rewrites() {
    const backendUrl = process.env.API_BASE_URL || 
      (process.env.NODE_ENV === 'production' ? 'http://backend:8000' : 'http://localhost:8000');
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/:path*`
      }
    ];
  },
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self' https://api.openai.com; camera 'self';"
          }
        ]
      }
    ];
  }
};

module.exports = withPWA(nextConfig);