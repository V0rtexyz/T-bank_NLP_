import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'T-Plexity - Агрегация инвестиционных новостей в реальном времени',
  description: 'Получайте мгновенные ответы об инвестиционных новостях с цитированием источников из Telegram',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  )
}

