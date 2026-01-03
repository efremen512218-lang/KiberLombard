'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function HomePage() {
  const [skinPrice, setSkinPrice] = useState<number>(10000)
  
  const calculateLoan = (price: number) => {
    return Math.round(price * 0.65)
  }
  
  const calculateBuyback = (price: number) => {
    const loan = price * 0.65
    return Math.round(price * 1.15 + loan * 0.25)
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-lg"></div>
            <span className="text-2xl font-bold neon-text">КиберЛомбард</span>
          </div>
          
          <nav className="hidden md:flex space-x-6">
            <Link href="#how-it-works" className="hover:text-cyber-blue transition">Как работает</Link>
            <Link href="#calculator" className="hover:text-cyber-blue transition">Калькулятор</Link>
            <Link href="#faq" className="hover:text-cyber-blue transition">FAQ</Link>
          </nav>
          
          <Link href="/auth/steam" className="cyber-button">
            Войти через Steam
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 left-10 w-72 h-72 bg-cyber-blue rounded-full filter blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-cyber-purple rounded-full filter blur-3xl animate-pulse delay-1000"></div>
        </div>
        
        <div className="relative z-10">
          <div className="inline-block mb-6 px-6 py-2 bg-cyber-blue/10 border border-cyber-blue/30 rounded-full">
            <span className="text-cyber-blue font-bold">🔥 Моментальный выкуп CS2 скинов</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 neon-text leading-tight">
            Превращай скины<br />в реальные деньги
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-3xl mx-auto">
            Получи <span className="text-green-400 font-bold">60-70%</span> от рыночной цены моментально.
          </p>
          <p className="text-lg md:text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Выкупи обратно в течение 7-30 дней по фиксированной цене или оставь нам.
          </p>
        
        <div className="flex flex-col md:flex-row gap-4 justify-center">
          <Link href="/cabinet/inventory" className="cyber-button text-lg">
            Начать сейчас
          </Link>
          <button className="bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg transition">
            Смотреть видео
          </button>
        </div>
        
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-16 max-w-5xl mx-auto">
            <div className="cyber-card hover:scale-105 transition-transform">
              <div className="text-5xl mb-3">💰</div>
              <div className="text-4xl font-bold text-cyber-blue mb-2">60-70%</div>
              <div className="text-gray-400">от рыночной цены</div>
            </div>
            <div className="cyber-card hover:scale-105 transition-transform">
              <div className="text-5xl mb-3">⚡</div>
              <div className="text-4xl font-bold text-cyber-purple mb-2">5 мин</div>
              <div className="text-gray-400">получение денег</div>
            </div>
            <div className="cyber-card hover:scale-105 transition-transform">
              <div className="text-5xl mb-3">🔄</div>
              <div className="text-4xl font-bold text-cyber-pink mb-2">7-30 дней</div>
              <div className="text-gray-400">срок выкупа</div>
            </div>
            <div className="cyber-card hover:scale-105 transition-transform">
              <div className="text-5xl mb-3">🎯</div>
              <div className="text-4xl font-bold text-green-400 mb-2">100%</div>
              <div className="text-gray-400">безопасность</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20 bg-gray-900/30">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-4 neon-text">Почему КиберЛомбард?</h2>
          <p className="text-center text-gray-400 mb-12 max-w-2xl mx-auto">
            Мы предлагаем уникальную модель выкупа с опционом обратного выкупа
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="cyber-card text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl flex items-center justify-center text-4xl mx-auto mb-4">
                💸
              </div>
              <h3 className="text-2xl font-bold mb-3">Моментальная выплата</h3>
              <p className="text-gray-400">
                Получи деньги на карту через СБП или ЮKassa за 5 минут после подтверждения трейда
              </p>
            </div>
            
            <div className="cyber-card text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center text-4xl mx-auto mb-4">
                🔒
              </div>
              <h3 className="text-2xl font-bold mb-3">Фиксированная цена</h3>
              <p className="text-gray-400">
                Цена выкупа фиксируется в момент сделки. Не зависит от колебаний рынка
              </p>
            </div>
            
            <div className="cyber-card text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl flex items-center justify-center text-4xl mx-auto mb-4">
                ⏰
              </div>
              <h3 className="text-2xl font-bold mb-3">Гибкий срок</h3>
              <p className="text-gray-400">
                Выбери срок опциона от 7 до 30 дней. Выкупи когда удобно или оставь нам
              </p>
            </div>
            
            <div className="cyber-card text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-orange-700 rounded-2xl flex items-center justify-center text-4xl mx-auto mb-4">
                📊
              </div>
              <h3 className="text-2xl font-bold mb-3">Честные цены</h3>
              <p className="text-gray-400">
                Агрегируем цены с Skinport, CSFloat и Steam Market для точной оценки
              </p>
            </div>
            
            <div className="cyber-card text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-red-500 to-red-700 rounded-2xl flex items-center justify-center text-4xl mx-auto mb-4">
                🛡️
              </div>
              <h3 className="text-2xl font-bold mb-3">Юридическая защита</h3>
              <p className="text-gray-400">
                Договор с электронной подписью. Полное соответствие законодательству РФ
              </p>
            </div>
            
            <div className="cyber-card text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-pink-500 to-pink-700 rounded-2xl flex items-center justify-center text-4xl mx-auto mb-4">
                🎮
              </div>
              <h3 className="text-2xl font-bold mb-3">Все скины CS2</h3>
              <p className="text-gray-400">
                Принимаем любые tradable предметы: оружие, ножи, перчатки, наклейки
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Calculator Section */}
      <section id="calculator" className="container mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-12 neon-text">Калькулятор выкупа</h2>
        
        <div className="max-w-2xl mx-auto cyber-card">
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Рыночная цена скина</label>
            <input
              type="number"
              value={skinPrice}
              onChange={(e) => setSkinPrice(Number(e.target.value))}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-cyber-blue focus:outline-none"
              placeholder="10000"
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-green-900/20 border border-green-500/50 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Ты получишь</div>
              <div className="text-3xl font-bold text-green-400">
                {calculateLoan(skinPrice).toLocaleString('ru-RU')} ₽
              </div>
            </div>
            
            <div className="bg-orange-900/20 border border-orange-500/50 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Выкуп обратно</div>
              <div className="text-3xl font-bold text-orange-400">
                {calculateBuyback(skinPrice).toLocaleString('ru-RU')} ₽
              </div>
            </div>
          </div>
          
          <div className="bg-blue-900/20 border border-blue-500/50 rounded-lg p-4 mb-6">
            <div className="text-sm text-gray-400 mb-2">Детали расчета:</div>
            <ul className="text-sm space-y-1">
              <li>• Выплата: 65% от рыночной цены</li>
              <li>• Выкуп: 115% от рыночной + премия опциона 25%</li>
              <li>• Срок: 7-30 дней (выбираешь сам)</li>
            </ul>
          </div>
          
          <Link href="/cabinet/inventory" className="cyber-button w-full text-center block">
            Выкупить мои скины
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="container mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-4 neon-text">Как это работает</h2>
        <p className="text-center text-gray-400 mb-12 max-w-2xl mx-auto">
          Простой процесс в 6 шагов. От входа до получения денег — всего 10 минут
        </p>
        
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div className="cyber-card relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-full flex items-center justify-center text-xl font-bold border-4 border-gray-900">
                1
              </div>
              <div className="text-4xl mb-3 mt-4">🎮</div>
              <h3 className="text-xl font-bold mb-2">Вход через Steam</h3>
              <p className="text-gray-400 text-sm">
                Безопасная авторизация через Steam OpenID. Мы не получаем доступ к твоему аккаунту
              </p>
            </div>
            
            <div className="cyber-card relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-full flex items-center justify-center text-xl font-bold border-4 border-gray-900">
                2
              </div>
              <div className="text-4xl mb-3 mt-4">🎒</div>
              <h3 className="text-xl font-bold mb-2">Выбери скины</h3>
              <p className="text-gray-400 text-sm">
                Мы покажем твой CS2 инвентарь с актуальными ценами с маркетов. Выбери что хочешь выкупить
              </p>
            </div>
            
            <div className="cyber-card relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-full flex items-center justify-center text-xl font-bold border-4 border-gray-900">
                3
              </div>
              <div className="text-4xl mb-3 mt-4">📱</div>
              <h3 className="text-xl font-bold mb-2">Верификация</h3>
              <p className="text-gray-400 text-sm">
                Подтверди телефон через SMS. Для сумм &gt;15к₽ нужен паспорт (115-ФЗ)
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="cyber-card relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-full flex items-center justify-center text-xl font-bold border-4 border-gray-900">
                4
              </div>
              <div className="text-4xl mb-3 mt-4">📝</div>
              <h3 className="text-xl font-bold mb-2">Подпиши договор</h3>
              <p className="text-gray-400 text-sm">
                SMS-код = простая электронная подпись. Договор имеет юридическую силу
              </p>
            </div>
            
            <div className="cyber-card relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-full flex items-center justify-center text-xl font-bold border-4 border-gray-900">
                5
              </div>
              <div className="text-4xl mb-3 mt-4">🔄</div>
              <h3 className="text-xl font-bold mb-2">Отправь трейд</h3>
              <p className="text-gray-400 text-sm">
                Прими trade offer от нашего бота в Steam. Скины будут переданы безопасно
              </p>
            </div>
            
            <div className="cyber-card relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-cyber-blue to-cyber-purple rounded-full flex items-center justify-center text-xl font-bold border-4 border-gray-900">
                6
              </div>
              <div className="text-4xl mb-3 mt-4">💰</div>
              <h3 className="text-xl font-bold mb-2">Получи деньги</h3>
              <p className="text-gray-400 text-sm">
                Деньги придут на карту через СБП или ЮKassa за 5 минут после подтверждения
              </p>
            </div>
          </div>
        </div>
        
        <div className="text-center mt-12">
          <Link href="/cabinet/inventory" className="cyber-button text-lg inline-block">
            Начать сейчас →
          </Link>
        </div>
      </section>

      {/* Comparison Section */}
      <section className="container mx-auto px-4 py-20 bg-gray-900/30">
        <h2 className="text-4xl font-bold text-center mb-4 neon-text">Сравнение с другими способами</h2>
        <p className="text-center text-gray-400 mb-12 max-w-2xl mx-auto">
          Почему КиберЛомбард выгоднее обычных маркетов
        </p>
        
        <div className="max-w-5xl mx-auto overflow-x-auto">
          <table className="w-full cyber-card">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left p-4">Параметр</th>
                <th className="text-center p-4 text-cyber-blue">КиберЛомбард</th>
                <th className="text-center p-4">Steam Market</th>
                <th className="text-center p-4">Skinport</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="p-4">Получение денег</td>
                <td className="text-center p-4 text-green-400 font-bold">5 минут</td>
                <td className="text-center p-4 text-gray-400">7 дней</td>
                <td className="text-center p-4 text-gray-400">1-3 дня</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="p-4">Комиссия</td>
                <td className="text-center p-4 text-green-400 font-bold">0%</td>
                <td className="text-center p-4 text-gray-400">13%</td>
                <td className="text-center p-4 text-gray-400">12%</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="p-4">Опцион выкупа</td>
                <td className="text-center p-4 text-green-400 font-bold">✅ Да</td>
                <td className="text-center p-4 text-gray-400">❌ Нет</td>
                <td className="text-center p-4 text-gray-400">❌ Нет</td>
              </tr>
              <tr className="border-b border-gray-800">
                <td className="p-4">Фиксированная цена</td>
                <td className="text-center p-4 text-green-400 font-bold">✅ Да</td>
                <td className="text-center p-4 text-gray-400">❌ Нет</td>
                <td className="text-center p-4 text-gray-400">❌ Нет</td>
              </tr>
              <tr>
                <td className="p-4">Вывод на карту РФ</td>
                <td className="text-center p-4 text-green-400 font-bold">✅ СБП</td>
                <td className="text-center p-4 text-gray-400">❌ Только Steam</td>
                <td className="text-center p-4 text-gray-400">⚠️ Сложно</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="container mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-4 neon-text">Частые вопросы</h2>
        <p className="text-center text-gray-400 mb-12 max-w-2xl mx-auto">
          Ответы на самые популярные вопросы о КиберЛомбарде
        </p>
        
        <div className="max-w-4xl mx-auto space-y-4">
          <details className="cyber-card group">
            <summary className="cursor-pointer font-bold text-lg flex justify-between items-center">
              <span>🤔 Это ломбард?</span>
              <span className="text-cyber-blue">+</span>
            </summary>
            <div className="mt-4 text-gray-400 border-t border-gray-800 pt-4">
              <p className="mb-2">
                <strong className="text-white">Нет, это НЕ ломбард.</strong> Это сервис выкупа цифровых прав на внутриигровые предметы CS2 с опционом обратного выкупа.
              </p>
              <p>
                Мы покупаем у вас права на скины, а вы получаете опцион выкупить их обратно в течение 7-30 дней по фиксированной цене. Это легальная модель по ст. 454 и 429.3 ГК РФ.
              </p>
            </div>
          </details>
          
          <details className="cyber-card group">
            <summary className="cursor-pointer font-bold text-lg flex justify-between items-center">
              <span>💰 Сколько я получу за скины?</span>
              <span className="text-cyber-blue">+</span>
            </summary>
            <div className="mt-4 text-gray-400 border-t border-gray-800 pt-4">
              <p className="mb-2">
                Вы получите <strong className="text-green-400">65%</strong> от средней рыночной цены ваших скинов.
              </p>
              <p className="mb-2">
                Мы агрегируем цены с Skinport, CSFloat и Steam Community Market, берем среднее значение и выплачиваем 65% от него.
              </p>
              <p>
                <strong>Пример:</strong> Скины стоят 10,000₽ → вы получаете 6,500₽ моментально.
              </p>
            </div>
          </details>
          
          <details className="cyber-card group">
            <summary className="cursor-pointer font-bold text-lg flex justify-between items-center">
              <span>🔄 Как работает выкуп обратно?</span>
              <span className="text-cyber-blue">+</span>
            </summary>
            <div className="mt-4 text-gray-400 border-t border-gray-800 pt-4">
              <p className="mb-2">
                При создании сделки фиксируется цена выкупа: <strong className="text-orange-400">115% от рыночной + премия опциона 25%</strong>.
              </p>
              <p className="mb-2">
                У вас есть 7-30 дней (выбираете сами), чтобы выкупить скины обратно по этой фиксированной цене.
              </p>
              <p className="mb-2">
                <strong>Пример:</strong> Скины на 10,000₽ → выкуп за 13,125₽ в течение 14 дней.
              </p>
              <p>
                Если не выкупите до срока — скины окончательно переходят нам. Возврат невозможен.
              </p>
            </div>
          </details>
          
          <details className="cyber-card group">
            <summary className="cursor-pointer font-bold text-lg flex justify-between items-center">
              <span>⏱️ Как быстро получу деньги?</span>
              <span className="text-cyber-blue">+</span>
            </summary>
            <div className="mt-4 text-gray-400 border-t border-gray-800 pt-4">
              <p className="mb-2">
                Деньги приходят на карту через <strong className="text-green-400">5 минут</strong> после того, как вы примете trade offer в Steam.
              </p>
              <p>
                Мы используем СБП (Система Быстрых Платежей) и ЮKassa для моментальных переводов на карты российских банков.
              </p>
            </div>
          </details>
          
          <details className="cyber-card group">
            <summary className="cursor-pointer font-bold text-lg flex justify-between items-center">
              <span>🛡️ Это безопасно?</span>
              <span className="text-cyber-blue">+</span>
            </summary>
            <div className="mt-4 text-gray-400 border-t border-gray-800 pt-4">
              <p className="mb-2">
                <strong className="text-green-400">Да, абсолютно безопасно.</strong> Мы используем официальный Steam API и trade offers.
              </p>
              <ul className="list-disc list-inside space-y-1 mb-2">
                <li>Авторизация через Steam OpenID (мы не получаем доступ к аккаунту)</li>
                <li>Все трейды через официальную систему Steam</li>
                <li>Договор с электронной подписью (ПЭП)</li>
                <li>Соответствие 115-ФЗ (ПОД/ФТ)</li>
              </ul>
              <p>
                Мы не можем украсть ваш аккаунт или скины. Все операции прозрачны и легальны.
              </p>
            </div>
          </details>
          
          <details className="cyber-card group">
            <summary className="cursor-pointer font-bold text-lg flex justify-between items-center">
              <span>📱 Нужен ли паспорт?</span>
              <span className="text-cyber-blue">+</span>
            </summary>
            <div className="mt-4 text-gray-400 border-t border-gray-800 pt-4">
              <p className="mb-2">
                Зависит от суммы сделки (требование 115-ФЗ):
              </p>
              <ul className="list-disc list-inside space-y-1">
                <li><strong>До 15,000₽:</strong> Только телефон + SMS-верификация</li>
                <li><strong>15,000 - 600,000₽:</strong> Паспорт (серия, номер, кем выдан)</li>
                <li><strong>Более 600,000₽:</strong> Фото паспорта + ручная модерация</li>
              </ul>
            </div>
          </details>
          
          <details className="cyber-card group">
            <summary className="cursor-pointer font-bold text-lg flex justify-between items-center">
              <span>⚠️ Какие риски?</span>
              <span className="text-cyber-blue">+</span>
            </summary>
            <div className="mt-4 text-gray-400 border-t border-gray-800 pt-4">
              <p className="mb-2">
                <strong className="text-red-400">Важно понимать:</strong>
              </p>
              <ul className="list-disc list-inside space-y-1 mb-2">
                <li>Скины CS2 = лицензия Valve, не вещь. Могут быть заблокированы/удалены</li>
                <li>Риск VAC-банов и трейд-блокировок полностью на вас</li>
                <li>После истечения срока опциона возврат невозможен</li>
                <li>При откате трейда Steam вы обязаны вернуть сумму + 20%</li>
              </ul>
              <p>
                Все риски подробно описаны в договоре. Мы требуем подтверждения понимания перед сделкой.
              </p>
            </div>
          </details>
          
          <details className="cyber-card group">
            <summary className="cursor-pointer font-bold text-lg flex justify-between items-center">
              <span>🎯 Какие скины принимаете?</span>
              <span className="text-cyber-blue">+</span>
            </summary>
            <div className="mt-4 text-gray-400 border-t border-gray-800 pt-4">
              <p className="mb-2">
                Мы принимаем <strong className="text-white">все tradable предметы CS2:</strong>
              </p>
              <ul className="list-disc list-inside space-y-1">
                <li>Оружие (винтовки, пистолеты, дробовики)</li>
                <li>Ножи и перчатки</li>
                <li>Наклейки и патчи</li>
                <li>Агенты</li>
                <li>Граффити и музыкальные наборы</li>
              </ul>
              <p className="mt-2">
                Главное условие — предмет должен быть tradable (без трейд-лока).
              </p>
            </div>
          </details>
        </div>
      </section>

      {/* Warning Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto bg-red-900/20 border-2 border-red-500/50 rounded-xl p-8">
          <div className="flex items-start gap-4 mb-6">
            <div className="text-5xl">⚠️</div>
            <div>
              <h3 className="text-3xl font-bold mb-2 text-red-400">ВАЖНО: Юридическая модель</h3>
              <p className="text-gray-400">Прочитайте внимательно перед использованием сервиса</p>
            </div>
          </div>
          
          <div className="space-y-4 text-gray-300">
            <div className="bg-gray-900/50 rounded-lg p-4">
              <p className="font-bold text-white mb-2">
                Это НЕ ломбард
              </p>
              <p>
                Это сервис выкупа цифровых прав на внутриигровые предметы CS2 с опционом обратного выкупа. 
                Мы работаем по ст. 454 и 429.3 ГК РФ (купля-продажа + опцион).
              </p>
            </div>
            
            <div className="bg-gray-900/50 rounded-lg p-4">
              <p className="font-bold text-white mb-2">
                Ключевые риски (полностью на клиенте):
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Скины CS2 = лицензия Valve, не вещь. Могут быть заблокированы/удалены Steam без компенсации</li>
                <li>Риск VAC-банов, трейд-блокировок и конфискации</li>
                <li>После истечения срока опциона возврат скинов/денег невозможен</li>
                <li>При откате трейда Steam: клиент обязан вернуть сумму + 20% (ст. 1102 ГК РФ)</li>
              </ul>
            </div>
            
            <div className="bg-gray-900/50 rounded-lg p-4">
              <p className="font-bold text-white mb-2">
                Юридическая защита:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Договор с простой электронной подписью (ПЭП через SMS)</li>
                <li>Полное раскрытие всех рисков</li>
                <li>Подсудность судам г. Москвы</li>
                <li>Соответствие 115-ФЗ (ПОД/ФТ)</li>
              </ul>
            </div>
            
            <p className="text-sm text-gray-400 mt-6 text-center">
              Продолжая использование сервиса, вы подтверждаете понимание и принятие всех рисков и условий.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-gray-900/50 backdrop-blur-sm mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h4 className="font-bold mb-4">КиберЛомбард CS2</h4>
              <p className="text-sm text-gray-400 mb-4">
                Выкуп цифровых прав на CS2 скины с опционом обратного выкупа
              </p>
              <Link href="/stats" className="text-sm text-cyber-blue hover:underline">
                📊 Статистика платформы
              </Link>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Документы</h4>
              <ul className="text-sm text-gray-400 space-y-2">
                <li><Link href="/docs/terms" className="hover:text-cyber-blue transition">Пользовательское соглашение</Link></li>
                <li><Link href="/docs/privacy" className="hover:text-cyber-blue transition">Политика конфиденциальности</Link></li>
                <li><Link href="/docs/risks" className="hover:text-cyber-blue transition">Раскрытие рисков</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Контакты</h4>
              <ul className="text-sm text-gray-400 space-y-2">
                <li>📧 Email: support@cyberlombard.ru</li>
                <li>💬 Telegram: @cyberlombard_support</li>
                <li>⏰ Пн-Пт 10:00-19:00 МСК</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            © 2025 КиберЛомбард CS2. Все права защищены.
          </div>
        </div>
      </footer>
    </div>
  )
}
