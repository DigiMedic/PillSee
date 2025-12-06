import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import GDPRNotice from '@/components/GDPRNotice'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter'
})

export const metadata: Metadata = {
  title: {
    default: 'PillSee - Informace o lécích',
    template: '%s | PillSee'
  },
  description: 'Anonymní AI asistent pro informace o českých lécích. Rozpoznejte léky z obrázků nebo se zeptejte v češtině.',
  keywords: ['léky', 'léčiva', 'zdraví', 'SÚKL', 'AI asistent', 'česky'],
  authors: [{ name: 'PillSee Team' }],
  creator: 'PillSee',
  publisher: 'PillSee',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || 'https://pillsee.vercel.app'),
  alternates: {
    canonical: '/',
    languages: {
      'cs-CZ': '/cs',
    },
  },
  openGraph: {
    type: 'website',
    locale: 'cs_CZ',
    url: '/',
    title: 'PillSee - Informace o lécích',
    description: 'Anonymní AI asistent pro informace o českých lécích',
    siteName: 'PillSee',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'PillSee - AI asistent pro léky',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'PillSee - Informace o lécích',
    description: 'Anonymní AI asistent pro informace o českých lécích',
    images: ['/twitter-image.png'],
  },
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'PillSee',
    startupImage: [
      {
        url: '/startup-screen.png',
        media: '(device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2)',
      },
    ],
  },
  other: {
    'mobile-web-app-capable': 'yes',
    'apple-mobile-web-app-capable': 'yes',
    'application-name': 'PillSee',
    'msapplication-TileColor': '#2563eb',
    'theme-color': '#2563eb',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="cs" className={inter.variable}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="apple-touch-icon" href="/icon-apple-touch.png" />
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body className={`${inter.className} bg-gray-50 min-h-screen antialiased`}>
        <div id="root">
          {children}
        </div>
        <GDPRNotice />
        <div id="modal-root" />
      </body>
    </html>
  )
}