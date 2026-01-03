'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

interface Deal {
  id: number
  market_total: number
  loan_amount: number
  buyback_price: number
  created_at: string
  option_expiry: string
  deal_status: 'PENDING' | 'ACTIVE' | 'BUYBACK' | 'DEFAULT' | 'CANCELLED'
  items_snapshot: any[]
}

export default function DealsPage() {
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    // TODO: Получить Steam ID из auth context
    const steamId = '76561198000000000' // Mock
    
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/deals?steam_id=${steamId}`)
      .then(res => res.json())
      .then(data => {
        setDeals(data || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error loading deals:', err)
        setLoading(false)
      })
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING': return 'text-yellow-400 border-yellow-400'
      case 'ACTIVE': return 'text-green-400 border-green-400'
      case 'BUYBACK': return 'text-blue-400 border-blue-400'
      case 'DEFAULT': return 'text-red-400 border-red-400'
      case 'CANCELLED': return 'text-gray-400 border-gray-400'
      default: return 'text-gray-400 border-gray-400'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'PENDING': return 'Ожидает трейда'
      case 'ACTIVE': return 'Активна'
      case 'BUYBACK': return 'Выкуплена'
      case 'DEFAULT': return 'Дефолт'
      case 'CANCELLED': return 'Отменена'
      default: return status
    }
  }

  const filteredDeals = deals.filter(deal => {
    if (filter === 'all') return true
    return deal.deal_status === filter.toUpperCase()
  })

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl">Загрузка сделок...</div>
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
          
          <nav className="flex space-x-6">
            <Link href="/cabinet/inventory" className="hover:text-cyber-blue transition">Инвентарь</Link>
            <Link href="/cabinet/deals" className="text-cyber-blue font-bold">Мои сделки</Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8 neon-text">Мои сделки</h1>

        {/* Filters */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg transition ${
              filter === 'all' 
                ? 'bg-cyber-blue text-white' 
                : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            Все ({deals.length})
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-4 py-2 rounded-lg transition ${
              filter === 'active' 
                ? 'bg-green-600 text-white' 
                : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            Активные
          </button>
          <button
            onClick={() => setFilter('buyback')}
            className={`px-4 py-2 rounded-lg transition ${
              filter === 'buyback' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            Выкупленные
          </button>
          <button
            onClick={() => setFilter('default')}
            className={`px-4 py-2 rounded-lg transition ${
              filter === 'default' 
                ? 'bg-red-600 text-white' 
                : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            Дефолт
          </button>
        </div>

        {/* Deals List */}
        {filteredDeals.length === 0 ? (
          <div className="cyber-card text-center py-12">
            <div className="text-gray-400 mb-4">Сделок пока нет</div>
            <Link href="/cabinet/inventory" className="cyber-button inline-block">
              Создать первую сделку
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredDeals.map(deal => (
              <Link
                key={deal.id}
                href={`/cabinet/deals/${deal.id}`}
                className="cyber-card block hover:border-cyber-blue transition"
              >
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl font-bold">Сделка #{deal.id}</span>
                      <span className={`text-sm px-3 py-1 rounded-full border ${getStatusColor(deal.deal_status)}`}>
                        {getStatusText(deal.deal_status)}
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-400">
                      Создана {formatDistanceToNow(new Date(deal.created_at), { addSuffix: true, locale: ru })}
                    </div>
                    
                    <div className="text-sm text-gray-400">
                      Предметов: {deal.items_snapshot.length}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-6">
                    <div>
                      <div className="text-xs text-gray-400 mb-1">Получено</div>
                      <div className="text-lg font-bold text-green-400">
                        {deal.loan_amount.toLocaleString('ru-RU')} ₽
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-gray-400 mb-1">Выкуп</div>
                      <div className="text-lg font-bold text-orange-400">
                        {deal.buyback_price.toLocaleString('ru-RU')} ₽
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-gray-400 mb-1">Срок до</div>
                      <div className="text-lg font-bold">
                        {new Date(deal.option_expiry).toLocaleDateString('ru-RU')}
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
