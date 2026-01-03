'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

export default function DealDetailPage() {
  const params = useParams()
  const dealId = params.id
  const [deal, setDeal] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/deals/${dealId}`)
      .then(res => res.json())
      .then(data => {
        setDeal(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error loading deal:', err)
        setLoading(false)
      })
  }, [dealId])

  const handleBuyback = async () => {
    // TODO: Интеграция с ЮKassa
    const paymentId = 'mock_payment_' + Date.now()
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/deals/${dealId}/buyback`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ payment_id: paymentId })
        }
      )
      
      if (response.ok) {
        alert('Выкуп оформлен! Ожидайте трейд.')
        window.location.reload()
      } else {
        const error = await response.json()
        alert(`Ошибка: ${error.detail}`)
      }
    } catch (error) {
      alert('Ошибка выкупа')
    }
  }

  // Подтвердить получение трейда (для тестирования)
  const handleConfirmTrade = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/deals/${dealId}/accept`,
        { method: 'POST' }
      )
      
      if (response.ok) {
        alert('Трейд подтверждён! Сделка активирована.')
        window.location.reload()
      } else {
        const error = await response.json()
        alert(`Ошибка: ${error.detail}`)
      }
    } catch (error) {
      alert('Ошибка подтверждения')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl">Загрузка сделки...</div>
      </div>
    )
  }

  if (!deal) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl mb-4">Сделка не найдена</div>
          <Link href="/cabinet/deals" className="cyber-button">
            Вернуться к сделкам
          </Link>
        </div>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING': return 'bg-yellow-900/20 border-yellow-400 text-yellow-400'
      case 'ACTIVE': return 'bg-green-900/20 border-green-400 text-green-400'
      case 'BUYBACK': return 'bg-blue-900/20 border-blue-400 text-blue-400'
      case 'DEFAULT': return 'bg-red-900/20 border-red-400 text-red-400'
      default: return 'bg-gray-900/20 border-gray-400 text-gray-400'
    }
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
          
          <Link href="/cabinet/deals" className="hover:text-cyber-blue transition">
            ← Все сделки
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2 neon-text">Сделка #{deal.id}</h1>
            <div className="text-gray-400">
              Создана {formatDistanceToNow(new Date(deal.created_at), { addSuffix: true, locale: ru })}
            </div>
          </div>
          
          <div className={`px-6 py-3 rounded-lg border-2 ${getStatusColor(deal.deal_status)}`}>
            <div className="text-2xl font-bold">
              {deal.deal_status === 'ACTIVE' && 'Активна'}
              {deal.deal_status === 'PENDING' && 'Ожидает трейда'}
              {deal.deal_status === 'BUYBACK' && 'Выкуплена'}
              {deal.deal_status === 'DEFAULT' && 'Дефолт'}
            </div>
          </div>
        </div>

        {/* Financial Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="cyber-card">
            <div className="text-sm text-gray-400 mb-1">Получено</div>
            <div className="text-2xl font-bold text-green-400">
              {(deal.loan_amount || 0).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽
            </div>
          </div>
          
          <div className="cyber-card">
            <div className="text-sm text-gray-400 mb-1">Цена выкупа</div>
            <div className="text-2xl font-bold text-orange-400">
              {(deal.buyback_price || 0).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽
            </div>
          </div>
          
          <div className="cyber-card">
            <div className="text-sm text-gray-400 mb-1">Срок до</div>
            <div className="text-2xl font-bold">
              {new Date(deal.option_expiry).toLocaleDateString('ru-RU')}
            </div>
            {deal.days_left !== null && deal.days_left >= 0 && (
              <div className="text-sm text-gray-400 mt-1">
                Осталось {deal.days_left} дней
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        {deal.deal_status === 'PENDING' && (
          <div className="cyber-card mb-8 bg-gradient-to-r from-yellow-900/20 to-orange-900/20 border-yellow-500">
            <div className="py-4">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-4xl">⏳</div>
                <div>
                  <h3 className="text-2xl font-bold text-yellow-400">Ожидается передача предметов</h3>
                  <p className="text-gray-400">Отправьте трейд-предложение для завершения сделки</p>
                </div>
              </div>
              
              <div className="bg-gray-800/50 rounded-lg p-4 mb-4">
                <h4 className="font-bold mb-2">Как передать предметы:</h4>
                <ol className="list-decimal list-inside space-y-2 text-gray-300">
                  <li>Откройте Steam и перейдите в инвентарь</li>
                  <li>Выберите предметы из сделки</li>
                  <li>Отправьте трейд на аккаунт КиберЛомбарда</li>
                  <li>После принятия трейда деньги поступят на ваш счёт</li>
                </ol>
              </div>
              
              {deal.initial_trade_url ? (
                <a
                  href={deal.initial_trade_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="cyber-button inline-block text-lg"
                >
                  🔗 Открыть трейд-предложение
                </a>
              ) : (
                <a
                  href="https://steamcommunity.com/tradeoffer/new/?partner=346262790&token=84ThNh2-"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="cyber-button inline-block text-lg"
                >
                  📤 Отправить трейд вручную
                </a>
              )}
              
              {/* Кнопка для тестирования - подтвердить получение */}
              <button
                onClick={handleConfirmTrade}
                className="ml-4 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg text-lg transition"
              >
                ✅ Подтвердить получение (тест)
              </button>
            </div>
          </div>
        )}

        {/* Блок для ACTIVE статуса - деньги отправлены */}
        {deal.deal_status === 'ACTIVE' && !deal.is_expired && (
          <div className="cyber-card mb-8 bg-gradient-to-r from-green-900/20 to-emerald-900/20 border-green-500">
            <div className="py-4">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-4xl">💰</div>
                <div>
                  <h3 className="text-2xl font-bold text-green-400">Деньги отправлены!</h3>
                  <p className="text-gray-400">
                    {(deal.loan_amount || 0).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽ отправлены на ваш счёт через СБП
                  </p>
                </div>
              </div>
              
              {deal.payout_transaction_id && (
                <div className="bg-gray-800/50 rounded-lg p-3 text-sm text-gray-400">
                  ID транзакции: {deal.payout_transaction_id}
                </div>
              )}
            </div>
          </div>
        )}

        {deal.can_buyback && (
          <div className="cyber-card mb-8 bg-gradient-to-r from-orange-900/20 to-red-900/20 border-orange-500">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-2xl font-bold mb-2">Выкупить скины обратно</h3>
                <p className="text-gray-400">
                  Оплатите {(deal.buyback_price || 0).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽ и получите скины обратно
                </p>
              </div>
              <button
                onClick={handleBuyback}
                className="cyber-button text-lg"
              >
                Выкупить за {(deal.buyback_price || 0).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽
              </button>
            </div>
          </div>
        )}

        {deal.is_expired && deal.deal_status === 'ACTIVE' && (
          <div className="cyber-card mb-8 bg-red-900/20 border-red-500">
            <div className="text-center py-6">
              <div className="text-4xl mb-4">⏰</div>
              <h3 className="text-2xl font-bold text-red-400 mb-2">Срок опциона истек</h3>
              <p className="text-gray-400">
                Скины окончательно перешли сервису. Возврат невозможен.
              </p>
            </div>
          </div>
        )}

        {/* Items */}
        <div className="cyber-card mb-8">
          <h3 className="text-2xl font-bold mb-4">Предметы ({deal.items_snapshot.length})</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {deal.items_snapshot.map((item: any, idx: number) => {
              // Извлекаем цену - может быть числом или объектом
              const marketPrice = typeof item.market_price === 'object' 
                ? (item.market_price?.instant_price || item.instant_price || 0)
                : (item.market_price || item.instant_price || 0)
              
              // Сумма выдачи = 40% от рыночной цены
              const loanPrice = item.loan_price || (marketPrice * 0.40)
              
              return (
                <div key={idx} className="bg-gray-800 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-2 truncate" title={item.market_hash_name}>
                    {item.market_hash_name}
                  </div>
                  <div className="text-sm font-bold text-green-400">
                    {loanPrice.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Contract */}
        <div className="cyber-card">
          <h3 className="text-2xl font-bold mb-4">Договор</h3>
          <a
            href={`/cabinet/deals/${deal.id}/contract`}
            target="_blank"
            rel="noopener noreferrer"
            className="cyber-button inline-block"
          >
            📄 Открыть договор
          </a>
        </div>
      </div>
    </div>
  )
}
