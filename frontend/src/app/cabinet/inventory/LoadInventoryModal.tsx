'use client'

import { useState } from 'react'

interface LoadInventoryModalProps {
  onLoad: (steamId: string) => void
  onClose: () => void
}

export default function LoadInventoryModal({ onLoad, onClose }: LoadInventoryModalProps) {
  const [link, setLink] = useState('')
  const [error, setError] = useState('')

  const handleLoad = () => {
    setError('')
    
    if (!link.trim()) {
      setError('Введите trade URL или Steam ID')
      return
    }
    
    let steamId = link.trim()
    let tradeUrl = ''
    
    // Парсинг различных форматов
    // 1. Trade offer: https://steamcommunity.com/tradeoffer/new/?partner=346262790&token=xxx
    if (steamId.includes('partner=')) {
      tradeUrl = steamId // Сохраняем полный trade URL
      const match = steamId.match(/partner=(\d+)/)
      if (match) {
        // Конвертация partner ID в Steam ID64
        const partnerId = parseInt(match[1])
        steamId = (BigInt(76561197960265728) + BigInt(partnerId)).toString()
      }
    }
    // 2. Profile: https://steamcommunity.com/profiles/76561198306528518
    else if (steamId.includes('profiles/')) {
      const match = steamId.match(/profiles\/(\d+)/)
      if (match) {
        steamId = match[1]
      }
    }
    // 3. Custom URL: https://steamcommunity.com/id/username
    else if (steamId.includes('/id/')) {
      setError('Пользовательские URL не поддерживаются. Используйте trade URL или числовой Steam ID.')
      return
    }
    // 4. Просто число
    else if (!/^\d+$/.test(steamId)) {
      setError('Неверный формат. Используйте trade URL или Steam ID (17 цифр).')
      return
    }
    
    // Проверка длины Steam ID64
    if (steamId.length < 17) {
      setError('Steam ID слишком короткий. Должен быть 17 цифр.')
      return
    }
    
    // Сохраняем trade URL в localStorage для будущего использования
    if (tradeUrl) {
      localStorage.setItem('trade_url', tradeUrl)
      console.log('Trade URL saved to localStorage:', tradeUrl)
    }
    
    console.log('Loading inventory for Steam ID:', steamId)
    onLoad(steamId)
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border-2 border-cyber-blue rounded-xl p-6 max-w-2xl w-full shadow-2xl shadow-cyber-blue/20">
        <h2 className="text-2xl font-bold mb-4 neon-text">Загрузить инвентарь</h2>
        
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-2">
              Вставьте ваш Trade URL (как на Lis-Skins)
            </label>
            <input
              type="text"
              value={link}
              onChange={(e) => setLink(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleLoad()}
              placeholder="https://steamcommunity.com/tradeoffer/new/?partner=346262790&token=..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-cyber-blue focus:outline-none"
              autoFocus
            />
            <div className="text-xs text-gray-400 mt-2">
              💡 Найдите ваш Trade URL в Steam: Инвентарь → Trade Offers → Who can send me Trade Offers?
            </div>
          </div>
          
          {error && (
            <div className="bg-red-900/30 border border-red-500 rounded-lg p-3 text-red-400 text-sm">
              {error}
            </div>
          )}
          
          <div className="bg-blue-900/20 border border-blue-500/50 rounded-lg p-4 text-sm">
            <div className="font-bold text-blue-400 mb-2">📌 Важно (как на Lis-Skins):</div>
            <ul className="space-y-2 text-gray-300">
              <li>✅ Используйте <strong>Trade URL</strong> (с partner и token)</li>
              <li>✅ Инвентарь должен быть <strong>публичным</strong></li>
              <li>✅ Аккаунт не должен иметь trade-банов</li>
            </ul>
            <div className="mt-3 text-xs text-gray-400">
              Где найти Trade URL: Steam → Инвентарь → Trade Offers → "Who can send me Trade Offers?" → скопируйте ссылку
            </div>
          </div>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition"
          >
            Отмена
          </button>
          <button
            onClick={handleLoad}
            className="flex-1 cyber-button"
          >
            Загрузить инвентарь
          </button>
        </div>
      </div>
    </div>
  )
}
