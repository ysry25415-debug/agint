/**
 * Product Hunter AI - Dashboard Layout
 * Main application layout with sidebar navigation
 */

import './globals.css'
import { Inter } from 'next/font/google'
import { Toaster } from 'sonner'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

export const metadata = {
  title: 'Product Hunter AI',
  description: 'Egyptian Electronics & Gadgets Market Intelligence',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased bg-gray-50`}>
        <div className="min-h-screen flex flex-col">
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="container mx-auto px-4 py-4">
              <h1 className="text-2xl font-bold text-gray-900">
                Product Hunter AI
              </h1>
              <p className="text-sm text-gray-500">
                Egyptian Electronics & Gadgets Market Intelligence
              </p>
            </div>
          </header>

          <main className="flex-1 container mx-auto px-4 py-6">
            {children}
          </main>

          <footer className="bg-white border-t border-gray-200 py-4">
            <div className="container mx-auto px-4 text-center text-sm text-gray-500">
              Product Hunter AI v0.1.0 | © 2026
            </div>
          </footer>

          <Toaster />
        </div>
      </body>
    </html>
  )
}