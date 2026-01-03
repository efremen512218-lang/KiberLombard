import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'КиберЛомбард CS2 - Выкуп скинов с опционом обратного выкупа',
  description: 'Моментальный выкуп CS2 скинов. Получи 60-70% от рыночной цены. Опцион обратного выкупа до 30 дней.',
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
