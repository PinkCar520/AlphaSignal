import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin();

/** @type {import('next').NextConfig} */
const nextConfig: import("next").NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: '/api/sse/:path*',
        destination: 'http://api:8001/api/:path*',
      },
      {
        source: '/api/stats',
        destination: 'http://api:8001/api/stats',
      },
    ];
  },
};

import { withSentryConfig } from '@sentry/nextjs';

export default withSentryConfig(
  withNextIntl(nextConfig),
  {
    // For all available options, see:
    // https://github.com/getsentry/sentry-webpack-plugin#options

    // Suppresses source map uploading logs during build
    silent: true,
    org: "alphasignal",
    project: "alphasignal-web",

    // Additional configurations
    widenClientFileUpload: true,
    disableLogger: true,
  }
);
