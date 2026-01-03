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
  instant_price?: number
  loan_amount?: number  // Сумма залога (50% от цены)
  is_acceptable?: boolean
  is_estimated?: boolean
  rarity?: string
  type?: string
}

interface UserProfile {
  steam_id: string
  steam_username: string
  steam_avatar: string
}

export default function InventoryPageV2() {
  const [items, setItems] = useState<SteamItem[]>([])
  const [filteredItems, setFilteredItems] = useState<SteamItem[]>([])
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [totalValue, setTotalValue] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'price-desc' | 'price-asc' | 'name'>('price-desc')
  const [filterRarity, setFilterRarity] = useState<string>('all')
  const [showLinkInput, setShowLinkInput] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)

  // Загрузка профиля пользователя
  useEffect(() => {
    const steamId = localStorage.getItem('steam_id')
    const username = localStorage.getItem('steam_username') || 'Пользователь'
    const avatar = localStorage.getItem('steam_avatar') || '/default-avatar.png'
    
    if (steamId) {
      setUserProfile({
        steam_id: steamId,
        steam_username: username,
        steam_avatar: avatar
      })
    }
  }, [])

  // Загрузка инвентаря
  const loadInventory = async (steamId?: string) => {
    const id = steamId || localStorage.getItem('steam_id') || '76561198000000000'
    
    try {
      setRefreshing(true)
      const response = await fetch(`http://localhost:8000/api/inventory/${id}`)
      const data = await response.json()
      
      setItems(data.items || [])
      setFilteredItems(data.items || [])
      setTotalValue(data.total_value || 0)
    } catch (err) {
      console.error('Error loading inventory:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadInventory()
  }, [])

  // Фильтрация и сортировка
  useEffect(() => {
    let filtered = [...items]

    filtered = filtered.filter(item => item.market_price >= 10)

    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.market_hash_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (filterRarity !== 'all') {
      filtered = filtered.filter(item => item.rarity === filterRarity)
    }

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

  const selectedItemsData = items.filter(item => selectedItems.has(item.assetid))
  
  const selectedValue = selectedItemsData
    .reduce((sum, item) => sum + (item.instant_price || item.market_price || 0), 0)
  
  // Используем loan_amount с бэкенда или считаем 40%
  const loanAmount = Math.round(
    selectedItemsData.reduce((sum, item) => {
      return sum + (item.loan_amount || (item.instant_price || item.market_price || 0) * 0.40)
    }, 0)
  )
  
  const buybackPrice = Math.round(loanAmount * 1.23) // 14 дней по умолчанию

  const getRarityColor = (rarity?: string) => {
    switch (rarity) {
      case 'Contraband': return 'bg-gradient-to-r from-yellow-500 to-orange-500'
      case 'Covert': return 'bg-gradient-to-r from-red-500 to-pink-500'
      case 'Classified': return 'bg-gradient-to-r from-pink-500 to-purple-500'
      case 'Restricted': return 'bg-gradient-to-r from-purple-500 to-blue-500'
      case 'Mil-Spec': return 'bg-gradient-to-r from-blue-500 to-cyan-500'
      default: return 'bg-gray-600'
    }
  }

  const uniqueRarities = Array.from(new Set(items.map(item => item.rarity).filter(Boolean)))

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a0e1a]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <div className="text-xl font-semibold text-white">Загрузка инвентаря...</div>
          <div className="text-sm text-gray-400 mt-2">Получаем данные из Steam</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0a0e1a]">
      {/* ПРОФЕССИОНАЛЬНЫЙ HEADER */}
      <header className="bg-[#0f1419] border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-[1920px] mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            {/* Лого */}
            <Link href="/" className="flex items-center gap-3">
              <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">К</span>
              </div>
              <span className="text-xl font-bold text-white">КиберЛомбард</span>
            </Link>

            {/* Навигация */}
            <nav className="flex items-center gap-8">
              <Link 
                href="/cabinet/inventory" 
                className="text-blue-400 font-medium hover:text-blue-300 transition"
              >
                Инвентарь
              </Link>
              <Link 
                href="/cabinet/deals" 
                className="text-gray-400 font-medium hover:text-white transition"
              >
                Мои сделки
              </Link>
              <Link 
                href="/docs/terms" 
                className="text-gray-400 font-medium hover:text-white transition"
              >
                FAQ
              </Link>
            </nav>

            {/* Профиль пользователя */}
            {userProfile ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center gap-3 bg-[#1a1f2e] hover:bg-[#252b3b] px-4 py-2 rounded-lg transition"
                >
                  <Image
                    src={userProfile.steam_avatar}
                    alt={userProfile.steam_username}
                    width={32}
                    height={32}
                    className="rounded-full"
                  />
                  <span className="text-white font-medium">{userProfile.steam_username}</span>
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Dropdown меню */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-[#1a1f2e] border border-gray-700 rounded-lg shadow-xl">
                    <Link
                      href="/cabinet/profile"
                      className="block px-4 py-3 text-gray-300 hover:bg-[#252b3b] hover:text-white transition"
                    >
                      Профиль
                    </Link>
                    <Link
                      href="/cabinet/deals"
                      className="block px-4 py-3 text-gray-300 hover:bg-[#252b3b] hover:text-white transition"
                    >
                      Мои сделки
                    </Link>
                    <button
                      onClick={() => {
                        localStorage.clear()
                        window.location.href = '/'
                      }}
                      className="block w-full text-left px-4 py-3 text-red-400 hover:bg-[#252b3b] transition"
                    >
                      Выйти
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => setShowLinkInput(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-2 rounded-lg transition"
              >
                Войти через Steam
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-[1920px] mx-auto px-6 py-6">
        {/* ПРОФЕССИОНАЛЬНЫЕ СТАТИСТИКИ */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-[#0f1419] border border-gray-800 rounded-xl p-5">
            <div className="text-sm text-gray-400 mb-2">Всего предметов</div>
            <div className="text-3xl font-bold text-white">{items.length}</div>
          </div>
          
          {/* Убрана общая стоимость по Steam */}
          
          <div className="bg-[#0f1419] border border-gray-800 rounded-xl p-5">
            <div className="text-sm text-gray-400 mb-2">Выбрано предметов</div>
            <div className="text-3xl font-bold text-purple-400">
              {selectedItems.size}
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl p-5">
            <div className="text-sm text-blue-100 mb-2">Сумма к выдаче</div>
            <div className="text-3xl font-bold text-white">
              {loanAmount.toLocaleString('ru-RU')} ₽
            </div>
          </div>
        </div>

        {/* ФИЛЬТРЫ И ПОИСК */}
        <div className="bg-[#0f1419] border border-gray-800 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-4">
            {/* Поиск */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Поиск по названию..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#1a1f2e] border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              />
            </div>

            {/* Сортировка */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-[#1a1f2e] border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="price-desc">Цена: дорогие</option>
              <option value="price-asc">Цена: дешевые</option>
              <option value="name">По названию</option>
            </select>

            {/* Фильтр редкости */}
            <select
              value={filterRarity}
              onChange={(e) => setFilterRarity(e.target.value)}
              className="bg-[#1a1f2e] border border-gray-700 rounded-lg px-4 py-2.5 text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="all">Все редкости</option>
              {uniqueRarities.map(rarity => (
                <option key={rarity} value={rarity}>{rarity}</option>
              ))}
            </select>

            {/* Кнопки выбора */}
            <button
              onClick={selectAll}
              className="bg-[#1a1f2e] hover:bg-[#252b3b] border border-gray-700 px-4 py-2.5 rounded-lg text-white transition"
            >
              Выбрать все
            </button>
            <button
              onClick={deselectAll}
              className="bg-[#1a1f2e] hover:bg-[#252b3b] border border-gray-700 px-4 py-2.5 rounded-lg text-white transition"
            >
              Сбросить
            </button>

            {/* Обновить инвентарь */}
            <button
              onClick={() => loadInventory()}
              disabled={refreshing}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 px-4 py-2.5 rounded-lg text-white transition flex items-center gap-2"
            >
              <svg className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {refreshing ? 'Обновление...' : 'Обновить'}
            </button>
          </div>
        </div>

        {/* СЕТКА ПРЕДМЕТОВ */}
        {filteredItems.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📦</div>
            <div className="text-2xl font-bold text-white mb-2">Предметы не найдены</div>
            <div className="text-gray-400">Попробуйте изменить фильтры или загрузить инвентарь</div>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-3 mb-24">
            {filteredItems.map(item => (
              <ItemCard
                key={item.assetid}
                item={item}
                isSelected={selectedItems.has(item.assetid)}
                onToggle={() => toggleItem(item.assetid)}
                getRarityColor={getRarityColor}
              />
            ))}
          </div>
        )}
      </div>

      {/* КОРЗИНА (НИЖНЯЯ ПАНЕЛЬ) */}
      {selectedItems.size > 0 && (
        <CartPanel
          selectedCount={selectedItems.size}
          selectedValue={selectedValue}
          loanAmount={loanAmount}
          buybackPrice={buybackPrice}
          onClear={deselectAll}
          selectedItems={Array.from(selectedItems)}
        />
      )}

      {/* МОДАЛКА ЗАГРУЗКИ */}
      {showLinkInput && (
        <LoadInventoryModal
          onLoad={(steamId) => {
            localStorage.setItem('steam_id', steamId)
            setShowLinkInput(false)
            loadInventory(steamId)
          }}
          onClose={() => setShowLinkInput(false)}
        />
      )}
    </div>
  )
}

// КОМПОНЕНТ КАРТОЧКИ ПРЕДМЕТА
function ItemCard({ 
  item, 
  isSelected, 
  onToggle, 
  getRarityColor 
}: { 
  item: SteamItem
  isSelected: boolean
  onToggle: () => void
  getRarityColor: (rarity?: string) => string
}) {
  // Используем loan_amount с бэкенда или считаем 40%
  const loanAmount = item.loan_amount || Math.round((item.instant_price || item.market_price || 0) * 0.40)

  return (
    <div
      onClick={onToggle}
      className={`relative bg-[#0f1419] border rounded-xl overflow-hidden cursor-pointer transition-all hover:scale-[1.02] hover:shadow-xl ${
        isSelected 
          ? 'border-blue-500 shadow-lg shadow-blue-500/20' 
          : 'border-gray-800 hover:border-gray-700'
      }`}
    >
      {/* Редкость (верхняя полоска) */}
      <div className={`h-1 ${getRarityColor(item.rarity)}`}></div>

      {/* Чекбокс */}
      <div className="absolute top-3 right-3 z-10">
        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition ${
          isSelected 
            ? 'bg-blue-500 border-blue-500' 
            : 'bg-transparent border-gray-600'
        }`}>
          {isSelected && (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </div>
      </div>

      {/* Изображение */}
      <div className="relative aspect-square bg-gradient-to-br from-gray-900 to-gray-800 p-4">
        <Image
          src={item.icon_url}
          alt={item.name}
          fill
          className="object-contain p-2"
        />
      </div>

      {/* Информация */}
      <div className="p-3">
        {/* Название */}
        <div className="text-sm font-medium text-white mb-2 line-clamp-2 min-h-[40px]">
          {item.name}
        </div>

        {/* Убрана цена Steam */}

        {/* Сумма к выдаче */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-2">
          <div className="text-xs text-blue-100 mb-1">Выдадим</div>
          <div className="text-lg font-bold text-white">
            {loanAmount.toLocaleString('ru-RU')} ₽
          </div>
        </div>

        {/* Бейдж редкости */}
        {item.rarity && (
          <div className={`mt-2 text-xs font-semibold text-white px-2 py-1 rounded ${getRarityColor(item.rarity)} text-center`}>
            {item.rarity}
          </div>
        )}
      </div>
    </div>
  )
}

// КОМПОНЕНТ КОРЗИНЫ
function CartPanel({
  selectedCount,
  selectedValue,
  loanAmount,
  buybackPrice,
  onClear,
  selectedItems
}: {
  selectedCount: number
  selectedValue: number
  loanAmount: number
  buybackPrice: number
  onClear: () => void
  selectedItems: string[]
}) {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-[#0f1419] border-t-2 border-blue-500 shadow-2xl z-50">
      <div className="max-w-[1920px] mx-auto px-6 py-5">
        <div className="flex items-center justify-between">
          {/* Статистика */}
          <div className="flex items-center gap-8">
            <div>
              <div className="text-sm text-gray-400 mb-1">Выбрано</div>
              <div className="text-2xl font-bold text-white">{selectedCount} шт</div>
            </div>
            
            {/* Убрана стоимость по Steam */}
            
            <div>
              <div className="text-sm text-gray-400 mb-1">Получите</div>
              <div className="text-2xl font-bold text-blue-400">
                {loanAmount.toLocaleString('ru-RU')} ₽
              </div>
            </div>
            
            <div>
              <div className="text-sm text-gray-400 mb-1">Выкуп</div>
              <div className="text-xl font-semibold text-purple-400">
                {buybackPrice.toLocaleString('ru-RU')} ₽
              </div>
            </div>
          </div>

          {/* Действия */}
          <div className="flex items-center gap-4">
            <button
              onClick={onClear}
              className="bg-gray-700 hover:bg-gray-600 text-white font-medium px-6 py-3 rounded-lg transition"
            >
              Очистить
            </button>
            <Link
              href={`/cabinet/quote?items=${selectedItems.join(',')}`}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold px-10 py-3 rounded-lg transition flex items-center gap-2"
            >
              Продолжить
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
