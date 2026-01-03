'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

export default function SteamCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const verifySteamAuth = async () => {
      try {
        // Получить все параметры OpenID
        const params: Record<string, string> = {}
        searchParams.forEach((value, key) => {
          params[key] = value
        })

        // Извлечь Steam ID из claimed_id
        const claimedId = params['openid.claimed_id']
        if (!claimedId) {
          console.error('No claimed_id in params:', params)
          setError('Steam не вернул ID. Попробуйте демо-режим.')
          return
        }

        const steamId = claimedId.split('/').pop()
        console.log('Steam ID extracted:', steamId)

        // Верифицировать через backend
        const response = await fetch(
          `http://localhost:8000/api/auth/steam/verify?steam_id=${steamId}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            }
          }
        )

        if (!response.ok) {
          const errorText = await response.text()
          console.error('Backend verification failed:', response.status, errorText)
          throw new Error(`Steam verification failed: ${response.status}`)
        }

        const user = await response.json()
        console.log('User verified:', user)

        // Сохранить в localStorage
        localStorage.setItem('user', JSON.stringify(user))
        localStorage.setItem('steam_id', user.steam_id)

        // Небольшая задержка чтобы localStorage успел сохраниться
        await new Promise(resolve => setTimeout(resolve, 100))

        // Редирект в инвентарь
        window.location.href = '/cabinet/inventory'
      } catch (error) {
        console.error('Steam auth error:', error)
        setError('Ошибка авторизации. Попробуйте демо-режим.')
      }
    }

    verifySteamAuth()
  }, [router, searchParams])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-cyber-dark to-gray-900">
        <div className="max-w-md mx-auto px-4">
          <div className="cyber-card text-center">
            <div className="text-6xl mb-4">❌</div>
            <h1 className="text-2xl font-bold mb-4 text-red-400">Ошибка авторизации</h1>
            <p className="text-gray-300 mb-6">{error}</p>
            <div className="flex flex-col gap-3">
              <a
                href="/"
                className="cyber-button"
              >
                На главную
              </a>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-cyber-dark to-gray-900">
      <div className="text-center">
        <div className="text-6xl mb-4 animate-pulse">🔄</div>
        <div className="text-2xl font-bold mb-2">Авторизация через Steam...</div>
        <div className="text-gray-400">Получаем данные профиля</div>
        <div className="mt-6">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-blue"></div>
        </div>
      </div>
    </div>
  )
}
