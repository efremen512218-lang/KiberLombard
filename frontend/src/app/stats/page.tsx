'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface PublicStats {
  total_deals: number
  active_deals: number
  total_volume: number
  avg_deal_amount: number
  buyback_rate: number
}

export default function StatsPage() {
  const [stats, setStats] = useState<PublicStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/stats/public`)
      .then(res => res.json())
      .then(data => {
        setStats(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error loading stats:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl">Загрузка статистики...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-lg"></div>
            <span className="text-2xl font-bold neon-text">КиберЛомбард</span>
          </Link>
          
          <Link href="/" className="hover:text-cyber-blue transition">
            ← На главную
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-4 neon-text text-center">Статистика платформы</h1>
        <p className="text-center text-gray-400 mb-12 max-w-2xl mx-auto">
          Прозрачная статистика работы КиберЛомбард CS2 в реальном времени
        </p>

        {stats && (
          <div className="max-w-6xl mx-auto">
            {/* Main Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
              <div className="cyber-card text-center hover:scale-105 transition-transform">
                <div className="text-5xl mb-4">📊</div>
                <div className="text-4xl font-bold text-cyber-blue mb-2">
                  {stats.total_deals.toLocaleString('ru-RU')}
                </div>
                <div className="text-gray-400">Всего сделок</div>
              </div>

              <div className="cyber-card text-center hover:scale-105 transition-transform">
                <div className="text-5xl mb-4">⚡</div>
                <div className="text-4xl font-bold text-green-400 mb-2">
                  {stats.active_deals.toLocaleString('ru-RU')}
                </div>
                <div className="text-gray-400">Активных сделок</div>
              </div>

              <div className="cyber-card text-center hover:scale-105 transition-transform">
                <div className="text-5xl mb-4">💰</div>
                <div className="text-4xl font-bold text-cyber-purple mb-2">
                  {(stats.total_volume / 1000000).toFixed(1)}M ₽
                </div>
                <div className="text-gray-400">Общий объем</div>
              </div>

              <div className="cyber-card text-center hover:scale-105 transition-transform">
                <div className="text-5xl mb-4">📈</div>
                <div className="text-4xl font-bold text-orange-400 mb-2">
                  {stats.avg_deal_amount.toLocaleString('ru-RU')} ₽
                </div>
                <div className="text-gray-400">Средняя сделка</div>
              </div>
            </div>

            {/* Buyback Rate */}
            <div className="cyber-card mb-12">
              <h2 className="text-2xl font-bold mb-6 text-center">Процент выкупов</h2>
              
              <div className="max-w-2xl mx-auto">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-400">Выкуплено обратно</span>
                  <span className="text-green-400 font-bold">{stats.buyback_rate.toFixed(1)}%</span>
                </div>
                
                <div className="w-full bg-gray-800 rounded-full h-8 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-green-700 h-full flex items-center justify-center text-white font-bold transition-all duration-1000"
                    style={{ width: `${stats.buyback_rate}%` }}
                  >
                    {stats.buyback_rate > 10 && `${stats.buyback_rate.toFixed(1)}%`}
                  </div>
                </div>
                
                <div className="flex justify-between mt-2 text-sm text-gray-500">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>
                
                <p className="text-center text-gray-400 mt-6">
                  {stats.buyback_rate > 50 
                    ? "Большинство клиентов выкупают скины обратно" 
                    : "Многие клиенты оставляют скины сервису"}
                </p>
              </div>
            </div>

            {/* Additional Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="cyber-card">
                <div className="text-3xl mb-3">🎯</div>
                <h3 className="text-xl font-bold mb-2">Прозрачность</h3>
                <p className="text-gray-400 text-sm">
                  Все сделки записываются в блокчейн... шутка, просто в базу данных. Но честно!
                </p>
              </div>

              <div className="cyber-card">
                <div className="text-3xl mb-3">⚡</div>
                <h3 className="text-xl font-bold mb-2">Скорость</h3>
                <p className="text-gray-400 text-sm">
                  Средняя скорость выплаты: 5 минут. От трейда до денег на карте.
                </p>
              </div>

              <div className="cyber-card">
                <div className="text-3xl mb-3">🛡️</div>
                <h3 className="text-xl font-bold mb-2">Надежность</h3>
                <p className="text-gray-400 text-sm">
                  100% выплат. Ни одной задержки. Ни одного отказа. Работаем честно.
                </p>
              </div>
            </div>

            {/* CTA */}
            <div className="text-center mt-12">
              <Link href="/cabinet/inventory" className="cyber-button text-lg inline-block">
                Создать свою сделку →
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
