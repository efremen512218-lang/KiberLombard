'use client'

import Link from 'next/link'

export default function SteamAuthPage() {
  const handleSteamLogin = () => {
    const returnUrl = `${window.location.origin}/auth/steam/callback`
    const params = new URLSearchParams({
      'openid.ns': 'http://specs.openid.net/auth/2.0',
      'openid.mode': 'checkid_setup',
      'openid.return_to': returnUrl,
      'openid.realm': window.location.origin,
      'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
      'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    })
    window.location.href = `https://steamcommunity.com/openid/login?${params.toString()}`
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-cyber-dark to-gray-900">
      <div className="max-w-2xl mx-auto px-4">
        <div className="cyber-card text-center">
          <div className="text-6xl mb-6">🎮</div>
          <h1 className="text-3xl font-bold mb-4 neon-text">Авторизация</h1>
          
          <p className="text-gray-300 mb-8">
            Войдите через Steam чтобы получить доступ к своему инвентарю
          </p>

          <button
            onClick={handleSteamLogin}
            className="cyber-button text-lg w-full md:w-auto px-12 py-4"
          >
            Войти через Steam
          </button>

          <div className="mt-8 pt-6 border-t border-gray-700">
            <Link href="/" className="text-cyber-blue hover:underline">
              ← Вернуться на главную
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
