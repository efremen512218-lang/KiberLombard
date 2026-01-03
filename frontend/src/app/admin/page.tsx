'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Deal {
  id: number
  user_id: number
  market_total: number
  loan_amount: number
  buyback_price: number
  created_at: string
  option_expiry: string
  deal_status: string
  items_snapshot: any[]
  kyc_snapshot: any
  payout_transaction_id: string | null
}

interface User {
  id: number
  steam_id: string
  steam_username: string
  phone: string | null
}

export default function AdminPage() {
  const [deals, setDeals] = useState<Deal[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [password, setPassword] = useState('')
  const [isAuth, setIsAuth] = useState(false)
  const [filter, setFilter] = useState('all')
  const [stats, setStats] = useState({ total: 0, pending: 0, active: 0, buyback: 0, default: 0 })

  // Простая авторизация
  const handleLogin = () => {
    if (password === 'admin123' || password === process.env.NEXT_PUBLIC_ADMIN_PASSWORD) {
      setIsAuth(true)
      localStorage.setItem('admin_auth', 'true')
    } else {
      alert('Неверный пароль')
    }
  }

  useEffect(() => {
    if (localStorage.getItem('admin_auth') === 'true') {
      setIsAuth(true)
    }
  }, [])

  useEffect(() => {
    if (!isAuth) return

    // Загрузить все сделки
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/deals`)
      .then(res => res.json())
      .then(data => {
        setDeals(data.deals || [])
        setUsers(data.users || [])
        
        // Статистика
        const s = { total: 0, pending: 0, active: 0, buyback: 0, default: 0 }
        data.deals?.forEach((d: Deal) => {
          s.total++
          if (d.deal_status === 'PENDING') s.pending++
          if (d.deal_status === 'ACTIVE') s.active++
          if (d.deal_status === 'BUYBACK') s.buyback++
          if (d.deal_status === 'DEFAULT') s.default++
        })
        setStats(s)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error:', err)
        setLoading(false)
      })
  }, [isAuth])

  const handleAction = async (dealId: number, action: 'accept' | 'reject' | 'default') => {
    const endpoint = action === 'accept' 
      ? `/api/deals/${dealId}/accept`
      : action === 'default'
      ? `/api/admin/deals/${dealId}/default`
      : `/api/admin/deals/${dealId}/cancel`

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, { method: 'POST' })
      if (res.ok) {
        alert(`Сделка #${dealId} ${action === 'accept' ? 'подтверждена' : action === 'default' ? 'переведена в дефолт' : 'отменена'}`)
        window.location.reload()
      } else {
        const err = await res.json()
        alert(`Ошибка: ${err.detail}`)
      }
    } catch (e) {
      alert('Ошибка сети')
    }
  }

  const getUser = (userId: number) => users.find(u => u.id === userId)

  const filteredDeals = deals.filter(d => {
    if (filter === 'all') return true
    return d.deal_status === filter.toUpperCase()
  })

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="bg-gray-800 p-8 rounded-xl max-w-md w-full">
          <h1 className="text-2xl font-bold text-white mb-6 text-center">🔐 Админ-панель</h1>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            placeholder="Пароль"
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white mb-4"
          />
          <button
            onClick={handleLogin}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg"
          >
            Войти
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-2xl font-bold">🎮 КиберЛомбард</Link>
            <span className="bg-red-600 px-3 py-1 rounded text-sm">ADMIN</span>
          </div>
          <button
            onClick={() => { localStorage.removeItem('admin_auth'); setIsAuth(false) }}
            className="text-gray-400 hover:text-white"
          >
            Выйти
          </button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-gray-800 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold">{stats.total}</div>
            <div className="text-gray-400 text-sm">Всего</div>
          </div>
          <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-yellow-400">{stats.pending}</div>
            <div className="text-gray-400 text-sm">Ожидают</div>
          </div>
          <div className="bg-green-900/30 border border-green-600 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-green-400">{stats.active}</div>
            <div className="text-gray-400 text-sm">Активные</div>
          </div>
          <div className="bg-blue-900/30 border border-blue-600 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-blue-400">{stats.buyback}</div>
            <div className="text-gray-400 text-sm">Выкуплены</div>
          </div>
          <div className="bg-red-900/30 border border-red-600 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-red-400">{stats.default}</div>
            <div className="text-gray-400 text-sm">Дефолт</div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6 flex-wrap">
          {['all', 'pending', 'active', 'buyback', 'default'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg ${filter === f ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'}`}
            >
              {f === 'all' ? 'Все' : f === 'pending' ? 'Ожидают' : f === 'active' ? 'Активные' : f === 'buyback' ? 'Выкуплены' : 'Дефолт'}
            </button>
          ))}
        </div>

        {/* Deals Table */}
        {loading ? (
          <div className="text-center py-12 text-gray-400">Загрузка...</div>
        ) : filteredDeals.length === 0 ? (
          <div className="text-center py-12 text-gray-400">Нет сделок</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full bg-gray-800 rounded-lg overflow-hidden">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left">ID</th>
                  <th className="px-4 py-3 text-left">Пользователь</th>
                  <th className="px-4 py-3 text-left">Сумма</th>
                  <th className="px-4 py-3 text-left">Выкуп</th>
                  <th className="px-4 py-3 text-left">Статус</th>
                  <th className="px-4 py-3 text-left">Дата</th>
                  <th className="px-4 py-3 text-left">Действия</th>
                </tr>
              </thead>
              <tbody>
                {filteredDeals.map(deal => {
                  const user = getUser(deal.user_id)
                  return (
                    <tr key={deal.id} className="border-t border-gray-700 hover:bg-gray-750">
                      <td className="px-4 py-3">#{deal.id}</td>
                      <td className="px-4 py-3">
                        <div className="font-medium">{user?.steam_username || 'Unknown'}</div>
                        <div className="text-xs text-gray-400">{deal.kyc_snapshot?.full_name || user?.steam_id}</div>
                        {deal.kyc_snapshot?.phone && (
                          <div className="text-xs text-gray-500">{deal.kyc_snapshot.phone}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-bold text-green-400">{deal.loan_amount.toLocaleString('ru-RU')} ₽</div>
                        <div className="text-xs text-gray-400">{deal.items_snapshot?.length || 0} скинов</div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-orange-400">{deal.buyback_price.toLocaleString('ru-RU')} ₽</div>
                        <div className="text-xs text-gray-400">до {new Date(deal.option_expiry).toLocaleDateString('ru-RU')}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          deal.deal_status === 'PENDING' ? 'bg-yellow-600' :
                          deal.deal_status === 'ACTIVE' ? 'bg-green-600' :
                          deal.deal_status === 'BUYBACK' ? 'bg-blue-600' :
                          'bg-red-600'
                        }`}>
                          {deal.deal_status}
                        </span>
                        {deal.payout_transaction_id && (
                          <div className="text-xs text-gray-500 mt-1">💰 {deal.payout_transaction_id.slice(0, 12)}...</div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-400">
                        {new Date(deal.created_at).toLocaleString('ru-RU')}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2 flex-wrap">
                          <Link
                            href={`/cabinet/deals/${deal.id}`}
                            className="bg-gray-600 hover:bg-gray-500 px-3 py-1 rounded text-sm"
                          >
                            👁️
                          </Link>
                          {deal.deal_status === 'PENDING' && (
                            <>
                              <button
                                onClick={() => handleAction(deal.id, 'accept')}
                                className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm"
                              >
                                ✅ Принять
                              </button>
                              <button
                                onClick={() => handleAction(deal.id, 'reject')}
                                className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
                              >
                                ❌
                              </button>
                            </>
                          )}
                          {deal.deal_status === 'ACTIVE' && (
                            <button
                              onClick={() => handleAction(deal.id, 'default')}
                              className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
                            >
                              Дефолт
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
