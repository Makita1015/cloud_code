import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ペットカルテ | トリミングサロン管理システム',
  description: 'トリミングサロン向けペットカルテ管理システム',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <header className="bg-white border-b border-gray-200 shadow-sm">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <a href="/" className="text-xl font-bold text-teal-600 hover:text-teal-700">
              ペットカルテ
            </a>
          </div>
        </header>
        <main className="max-w-4xl mx-auto px-4 py-6">
          {children}
        </main>
      </body>
    </html>
  )
}
