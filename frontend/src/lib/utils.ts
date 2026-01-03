import { type ClassValue, clsx } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatPrice(price: number): string {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price)
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function calculateLoanAmount(marketPrice: number): number {
  return Math.round(marketPrice * 0.65)
}

export function calculateBuybackPrice(marketPrice: number): number {
  const loanAmount = marketPrice * 0.65
  return Math.round(marketPrice * 1.15 + loanAmount * 0.25)
}

export function getDaysLeft(expiryDate: string | Date): number {
  const now = new Date()
  const expiry = new Date(expiryDate)
  const diff = expiry.getTime() - now.getTime()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

export function isExpired(expiryDate: string | Date): boolean {
  return new Date(expiryDate) < new Date()
}
