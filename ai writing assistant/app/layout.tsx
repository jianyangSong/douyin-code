import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '小红书AI文案生成工具',
  description: '基于AI的小红书文案生成工具，一键生成多种风格文案',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body className={`${inter.className} min-h-screen`}>
        {children}
      </body>
    </html>
  )
} 