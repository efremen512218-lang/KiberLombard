'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import LoadInventoryModal from './LoadInventoryModal'

interface SteamItem {
  assetid: string
  market_hash_name: string
  name: string
  icon_url: string
  market_price: number
  is_estimated?: boolean  // Это оценка, не реальная цена
  rarity?: string
  type?: string
}

export default function InventoryPage() {
  const [items, setItems] = useState<SteamItem[]>([])
  const [filteredItems, setFilteredItems] = useState<SteamItem[]>([])
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [totalValue, setTotalValue] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'price-desc' | 'price-asc' | 'name'>('price-desc')
  const [filterRarity, setFilterRarity] = useState<string>('all')
  const [showLinkInput, setShowLinkInput] = useState(false)
  const [inventoryLink, setInventoryLink] = useState('')
  const [loadingLink, setLoadingLink] = useState(false)

  useEffect(() => {
    // Получить Steam ID из localStorage
    const steamId = localStorage.getItem('steam_id') || '76561198000000000'
    
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/inventory/${steamId}`)
      .then(res => res.json())
      .then(data => {
        setItems(data.items || [])
        setFilteredItems(data.items || [])
        setTotalValue(data.total_value || 0)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error loading inventory:', err)
        setLoading(false)
      })
  }, [])

  // Фильтрация и сортировка
  useEffect(() => {
    let filtered = [...items]

    // Фильтр: только предметы с ценой >= 10₽
    filtered = filtered.filter(item => item.market_price >= 10)

    // Поиск
    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.market_hash_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Фильтр по редкости
    if (filterRarity !== 'all') {
      filtered = filtered.filter(item => item.rarity === filterRarity)
    }

    // Сортировка
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price-desc':
          return b.market_price - a.market_price
        case 'price-asc':
          return a.market_price - b.market_price
        case 'name':
          return a.name.localeCompare(b.name)
        default:
          return 0
      }
    })

    setFilteredItems(filtered)
  }, [items, searchQuery, sortBy, filterRarity])

  const toggleItem = (assetid: string) => {
    const newSelected = new Set(selectedItems)
    if (newSelected.has(assetid)) {
      newSelected.delete(assetid)
    } else {
      newSelected.add(assetid)
    }
    setSelectedItems(newSelected)
  }

  const selectAll = () => {
    setSelectedItems(new Set(filteredItems.map(item => item.assetid)))
  }

  const deselectAll = () => {
    setSelectedItems(new Set())
  }

  const selectedValue = items
    .filter(item => selectedItems.has(item.assetid))
    .reduce((sum, item) => sum + item.market_price, 0)
  
  // НОВАЯ ЛОГИКА:
  // Steam Market: 16,800₽ → Залог: 5,000₽ (30%) → Выкуп: 10,000₽ (60%)
  
  // Залог = 30% от Steam Market (консервативно)
  const loanAmount = Math.round(selectedValue * 0.30)
  
  // Выкуп = 60% от Steam Market (близко к цене скупки Lis-Skins)
  const buybackPrice = Math.round(selectedValue * 0.60)
  
  // Прибыль если выкупят
  const profitIfBuyback = buybackPrice - loanAmount
  
  // Прибыль если не выкупят (продаем на Lis-Skins ~64% от Steam)
  const lisskinsSellEstimate = Math.round(selectedValue * 0.64)
  const profitIfSell = lisskinsSellEstimate - loanAmount
  
  // Процентная ставка (за 30 дней)
  const optionDays = 30
  const dailyRate = ((profitIfBuyback / loanAmount / optionDays) * 100).toFixed(2)
  const monthlyRate = ((profitIfBuyback / loanAmount) * 100).toFixed(1)
  const yearlyRate = ((profitIfBuyback / loanAmount) * (365 / optionDays) * 100).toFixed(0)

  const getRarityColor = (rarity?: string) => {
    switch (rarity) {
      case 'Contraband': return 'from-yellow-500 to-orange-600'
      case 'Covert': return 'from-red-500 to-pink-600'
      case 'Classified': return 'from-pink-500 to-purple-600'
      case 'Restricted': return 'from-purple-500 to-blue-600'
      case 'Mil-Spec': return 'from-blue-500 to-cyan-600'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  const uniqueRarities = Array.from(new Set(items.map(item => item.rarity).filter(Boolean)))

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-cyber-dark to-gray-900">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-pulse">🎒</div>
          <div className="text-2xl font-bold mb-2">Загрузка инвентаря...</div>
          <div className="text-gray-400">Получаем данные из Steam</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyber-dark to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center mb-4">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-lg"></div>
              <span className="text-2xl font-bold neon-text">КиберЛомбард</span>
            </Link>
            
            <div className="flex items-center gap-4">
              <nav className="flex space-x-6">
                <Link href="/cabinet/inventory" className="text-cyber-blue font-bold">Инвентарь</Link>
                <Link href="/cabinet/deals" className="hover:text-cyber-blue transition">Мои сделки</Link>
              </nav>
              
              <button
                onClick={() => setShowLinkInput(true)}
                className="bg-cyber-blue hover:bg-cyber-purple text-white font-bold py-2 px-4 rounded-lg transition text-sm"
              >
                📥 Загрузить инвентарь
              </button>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="🔍 Поиск по названию..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-cyber-blue focus:outline-none"
              />
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-cyber-blue focus:outline-none"
            >
              <option value="price-desc">Цена: дорогие</option>
              <option value="price-asc">Цена: дешевые</option>
              <option value="name">По названию</option>
            </select>

            {/* Rarity Filter */}
            <select
              value={filterRarity}
              onChange={(e) => setFilterRarity(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-cyber-blue focus:outline-none"
            >
              <option value="all">Все редкости</option>
              {uniqueRarities.map(rarity => (
                <option key={rarity} value={rarity}>{rarity}</option>
              ))}
            </select>

            {/* Select Actions */}
            <div className="flex gap-2">
              <button
                onClick={selectAll}
                className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition text-sm"
              >
                Выбрать все
              </button>
              <button
                onClick={deselectAll}
                className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition text-sm"
              >
                Сбросить
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-xl p-4 hover:border-cyber-blue transition">
            <div className="text-sm text-gray-400 mb-1">Всего предметов</div>
            <div className="text-3xl font-bold">{items.length}</div>
          </div>
          
          <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-xl p-4 hover:border-cyber-blue transition">
            <div className="text-sm text-gray-400 mb-1">Общая стоимость</div>
            <div className="text-3xl font-bold text-cyber-blue">
              {totalValue.toLocaleString('ru-RU')} ₽
            </div>
          </div>
          
          <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-xl p-4 hover:border-green-500 transition">
            <div className="text-sm text-gray-400 mb-1">Выбрано</div>
            <div className="text-3xl font-bold text-green-400">
              {selectedItems.size}
            </div>
          </div>
          
          <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-xl p-4 hover:border-green-500 transition">
            <div className="text-sm text-gray-400 mb-1">Получишь</div>
            <div className="text-3xl font-bold text-green-400">
              {loanAmount.toLocaleString('ru-RU')} ₽
            </div>
          </div>
        </div>

        {/* Items Grid */}
        {filteredItems.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">😔</div>
            <div className="text-2xl font-bold mb-2">Ничего не найдено</div>
            <div className="text-gray-400">Попробуйте изменить фильтры или поиск</div>
          </div>
        ) : (
          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3 mb-24">
            {filteredItems.map(item => (
              <div
                key={item.assetid}
                onClick={() => toggleItem(item.assetid)}
                className={`relative bg-gray-900/50 backdrop-blur-sm border rounded-lg p-2 cursor-pointer transition-all hover:scale-105 ${
                  selectedItems.has(item.assetid) 
                    ? 'border-cyber-blue bg-cyber-blue/10 shadow-lg shadow-cyber-blue/50' 
                    : 'border-gray-800 hover:border-gray-600'
                }`}
              >
                {/* Rarity Gradient */}
                <div className={`absolute top-0 left-0 right-0 h-1 rounded-t-xl bg-gradient-to-r ${getRarityColor(item.rarity)}`}></div>
                
                {/* Selected Badge */}
                {selectedItems.has(item.assetid) && (
                  <div className="absolute top-2 right-2 bg-cyber-blue text-white text-xs font-bold px-2 py-1 rounded-full">
                    ✓
                  </div>
                )}

                {/* Image */}
                <div className="relative aspect-square mb-2 bg-gray-800/50 rounded-lg overflow-hidden">
                  <Image
                    src={item.icon_url}
                    alt={item.name}
                    fill
                    className="object-contain p-1"
                  />
                </div>
                
                {/* Name */}
                <div className="text-xs font-medium mb-1 line-clamp-2 min-h-[32px]" title={item.market_hash_name}>
                  {item.name}
                </div>
                
                {/* Prices */}
                <div className="space-y-1">
                  {/* Steam Market Price */}
                  <div className="flex justify-between items-center">
                    <div className="text-xs text-gray-400">Steam:</div>
                    <div className={`text-xs font-bold ${item.market_price > 0 ? (item.is_estimated ? 'text-yellow-400' : 'text-gray-300') : 'text-gray-600'}`}>
                      {item.market_price > 0 ? `${item.is_estimated ? '~' : ''}${item.market_price.toLocaleString('ru-RU')} ₽` : 'Недоступно'}
                    </div>
                  </div>
                  
                  {/* Estimated Sell Price (Steam Market) */}
                  {item.market_price > 0 && item.is_estimated && (
                    <div className="flex justify-between items-center">
                      <div className="text-xs text-yellow-400">⚠️ Оценка</div>
                    </div>
                  )}
                  
                  {/* Loan Amount (30% от Steam) */}
                  {item.market_price > 0 && (
                    <div className="flex justify-between items-center pt-1 border-t border-gray-700">
                      <div className="text-xs text-gray-400">Залог:</div>
                      <div className={`text-sm font-bold ${item.is_estimated ? 'text-yellow-400' : 'text-cyber-blue'}`}>
                        {item.is_estimated ? '~' : ''}{(item.market_price * 0.3).toLocaleString('ru-RU')} ₽
                      </div>
                    </div>
                  )}
                  
                  {/* Rarity Badge */}
                  {item.rarity && (
                    <div className={`text-xs px-1 py-0.5 rounded bg-gradient-to-r ${getRarityColor(item.rarity)} text-white font-bold text-center mt-1`}>
                      {item.rarity}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Action Panel */}
        {selectedItems.size > 0 && (
          <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 border-t-2 border-cyber-blue shadow-2xl shadow-cyber-blue/20 backdrop-blur-lg z-50">
            <div className="container mx-auto px-4 py-6">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 flex-1">
                  <div className="text-center md:text-left">
                    <div className="text-xs text-gray-400 mb-1">Выбрано</div>
                    <div className="text-2xl font-bold text-white">{selectedItems.size} шт</div>
                  </div>
                  
                  <div className="text-center md:text-left">
                    <div className="text-xs text-gray-400 mb-1">📊 Steam Market</div>
                    <div className="text-xl font-bold text-gray-300">
                      {selectedValue.toLocaleString('ru-RU')} ₽
                    </div>
                  </div>
                  
                  <div className="text-center md:text-left">
                    <div className="text-xs text-gray-400 mb-1">💰 Залог (30%)</div>
                    <div className="text-2xl font-bold text-cyber-blue">
                      {loanAmount.toLocaleString('ru-RU')} ₽
                    </div>
                  </div>
                  
                  <div className="text-center md:text-left">
                    <div className="text-xs text-gray-400 mb-1">🔄 Выкуп (60%)</div>
                    <div className="text-2xl font-bold text-orange-400">
                      {buybackPrice.toLocaleString('ru-RU')} ₽
                    </div>
                  </div>
                  
                  <div className="text-center md:text-left">
                    <div className="text-xs text-gray-400 mb-1">📈 Прибыль</div>
                    <div className="text-2xl font-bold text-green-400">
                      {profitIfBuyback.toLocaleString('ru-RU')} ₽
                    </div>
                  </div>
                  
                  <div className="text-center md:text-left">
                    <div className="text-xs text-gray-400 mb-1">⚡ Ставка</div>
                    <div className="text-xl font-bold text-yellow-400">
                      {dailyRate}% / день
                    </div>
                    <div className="text-xs text-gray-400">
                      {monthlyRate}% / мес ({yearlyRate}% год)
                    </div>
                  </div>
                </div>
                
                {/* Profit Info */}
                <div className="text-center md:text-right">
                  <div className="text-xs text-gray-400 mb-1">💎 Если не выкупят</div>
                  <div className="text-xl font-bold text-purple-400">
                    {profitIfSell.toLocaleString('ru-RU')} ₽
                  </div>
                  <div className="text-xs text-gray-400">
                    Продажа на Lis-Skins
                  </div>
                </div>
                
                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={deselectAll}
                    className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition"
                  >
                    Сбросить
                  </button>
                  <Link 
                    href={`/cabinet/quote?items=${Array.from(selectedItems).join(',')}`}
                    className="bg-gradient-to-r from-cyber-blue to-cyber-purple text-white font-bold py-3 px-8 rounded-lg transition-all duration-300 hover:scale-105 hover:shadow-lg shadow-cyber-blue/50 flex items-center gap-2"
                  >
                    Продолжить
                    <span className="text-xl">→</span>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Load Inventory Modal */}
      {showLinkInput && (
        <LoadInventoryModal
          onLoad={(steamId) => {
            console.log('Loading inventory for:', steamId)
            localStorage.setItem('steam_id', steamId)
            setShowLinkInput(false)
            setLoading(true)
            
            // Перезагрузить инвентарь
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            fetch(`${apiUrl}/api/inventory/${steamId}`)
              .then(res => res.json())
              .then(data => {
                setItems(data.items || [])
                setFilteredItems(data.items || [])
                setTotalValue(data.total_value || 0)
                setLoading(false)
              })
              .catch(err => {
                console.error('Error loading inventory:', err)
                setLoading(false)
              })
          }}
          onClose={() => setShowLinkInput(false)}
        />
      )}
    </div>
  )
}
