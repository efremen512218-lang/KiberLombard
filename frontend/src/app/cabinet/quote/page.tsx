'use client'

import { useState, useEffect, useRef } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'

interface PassportOCRData {
  full_name: string
  surname: string
  name: string
  patronymic: string
  series: string
  number: string
  birth_date: string
  birth_place: string
  issue_date: string
  department_code: string
  gender: string
  confidence: number
  raw_text: string
}

export default function QuotePage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [quote, setQuote] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [step, setStep] = useState<'quote' | 'kyc' | 'sign'>('quote')
  const [optionDays, setOptionDays] = useState(14)
  
  // KYC данные
  const [phone, setPhone] = useState('')
  const [passportPhoto, setPassportPhoto] = useState<string | null>(null)
  const [registrationPhoto, setRegistrationPhoto] = useState<string | null>(null)
  const [passportData, setPassportData] = useState<PassportOCRData | null>(null)
  const [registrationAddress, setRegistrationAddress] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const registrationInputRef = useRef<HTMLInputElement>(null)
  
  // Договор
  const [acceptTerms, setAcceptTerms] = useState(false)
  const [dealCreating, setDealCreating] = useState(false)

  // Генерация номера договора
  const contractNumber = `КЛ-${new Date().getFullYear()}-${String(Date.now()).slice(-6)}`

  // Загрузить quote
  useEffect(() => {
    const itemIds = searchParams.get('items')?.split(',') || []
    const steamId = localStorage.getItem('steam_id') || '76561198000000000'
    
    if (itemIds.length === 0) {
      router.push('/cabinet/inventory')
      return
    }
    
    setLoading(true)
    
    fetch(`http://localhost:8000/api/quote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        steam_id: steamId,
        asset_ids: itemIds,
        option_days: 14
      })
    })
      .then(res => res.json())
      .then(data => {
        setQuote(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error loading quote:', err)
        setLoading(false)
      })
  }, [searchParams])

  // Расчёт процентов
  const calculateInterestRate = (days: number) => {
    const terms: any = {
      7: { interest: 0.10, premium: 0.05 },
      14: { interest: 0.15, premium: 0.07 },
      21: { interest: 0.20, premium: 0.09 },
      30: { interest: 0.25, premium: 0.10 }
    }
    
    const sortedDays = Object.keys(terms).map(Number).sort((a, b) => a - b)
    let lower = sortedDays[0]
    let upper = sortedDays[sortedDays.length - 1]
    
    for (let i = 0; i < sortedDays.length - 1; i++) {
      if (days >= sortedDays[i] && days <= sortedDays[i + 1]) {
        lower = sortedDays[i]
        upper = sortedDays[i + 1]
        break
      }
    }
    
    const ratio = (days - lower) / (upper - lower)
    const interest = terms[lower].interest + ratio * (terms[upper].interest - terms[lower].interest)
    const premium = terms[lower].premium + ratio * (terms[upper].premium - terms[lower].premium)
    
    return { interest, premium, total: interest + premium }
  }

  const loanAmount = quote?.loan_amount || 0
  const interestRate = calculateInterestRate(optionDays)
  const buybackPrice = loanAmount * (1 + interestRate.total)
  const overpayment = buybackPrice - loanAmount
  
  const expiryDate = new Date()
  expiryDate.setDate(expiryDate.getDate() + optionDays)
  
  const formatMoney = (value: number) => {
    return value.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' })
  }

  // Загрузка фото паспорта (без OCR - просто сохраняем фото)
  const handlePassportUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = async () => {
        const base64 = reader.result as string
        setPassportPhoto(base64)
        
        // Инициализируем пустые данные для ручного ввода
        if (!passportData) {
          setPassportData({
            full_name: '',
            surname: '',
            name: '',
            patronymic: '',
            series: '',
            number: '',
            birth_date: '',
            birth_place: '',
            issue_date: '',
            department_code: '',
            gender: '',
            confidence: 1,
            raw_text: ''
          })
        }
      }
      reader.readAsDataURL(file)
    }
  }

  // Загрузка фото прописки
  const handleRegistrationUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => setRegistrationPhoto(reader.result as string)
      reader.readAsDataURL(file)
    }
  }

  // Подтвердить KYC
  const confirmKyc = () => {
    if (!passportPhoto || !registrationPhoto) {
      alert('Загрузите оба фото паспорта')
      return
    }
    setStep('sign')
  }

  // Создать сделку
  const createDeal = async () => {
    setDealCreating(true)
    
    try {
      const itemIds = searchParams.get('items')?.split(',') || []
      const steamId = localStorage.getItem('steam_id') || '76561198000000000'
      const steamUsername = localStorage.getItem('steam_username') || ''
      
      const response = await fetch(`http://localhost:8000/api/deals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quote_request: {
            steam_id: steamId,
            asset_ids: itemIds,
            option_days: optionDays
          },
          sms_code: '000000',
          accept_terms: acceptTerms,
          skip_verification: true,
          kyc_data: {
            full_name: passportData?.full_name || '',
            passport_series: passportData?.series || '',
            passport_number: passportData?.number || '',
            birth_date: passportData?.birth_date || '',
            department_code: passportData?.department_code || '',
            registration_address: registrationAddress || '',
            phone: phone || ''
          }
        })
      })
      
      if (response.ok) {
        const deal = await response.json()
        router.push(`/cabinet/deals/${deal.id}`)
      } else {
        const error = await response.json()
        alert(`Ошибка: ${error.detail}`)
      }
    } catch (error) {
      alert('Ошибка создания сделки')
    } finally {
      setDealCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a0e1a]">
        <div className="text-2xl text-white">Расчет условий...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0a0e1a]">
      {/* Header */}
      <header className="border-b border-gray-800 bg-[#0f1419]">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">К</span>
            </div>
            <span className="text-2xl font-bold text-white">КиберЛомбард</span>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Progress */}
        <div className="flex justify-between mb-8">
          {['Условия', 'Верификация', 'Договор'].map((label, i) => (
            <div key={i} className={`flex-1 text-center ${
              (i === 0 && step === 'quote') || 
              (i === 1 && step === 'kyc') || 
              (i === 2 && step === 'sign') 
                ? 'text-blue-400' : 'text-gray-500'
            }`}>
              <div className="text-2xl mb-2">{i + 1}</div>
              <div>{label}</div>
            </div>
          ))}
        </div>

        {/* Step 1: Quote */}
        {step === 'quote' && (
          <div className="space-y-6">
            <h1 className="text-4xl font-bold text-white">Условия сделки</h1>
            
            <div className="bg-[#0f1419] border border-gray-800 rounded-xl p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-green-900/20 border border-green-500/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">💰 Ты получишь</div>
                  <div className="text-3xl font-bold text-green-400">{formatMoney(loanAmount)} ₽</div>
                </div>
                
                <div className="bg-orange-900/20 border border-orange-500/50 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">🔄 Выкуп</div>
                  <div className="text-3xl font-bold text-orange-400">{formatMoney(buybackPrice)} ₽</div>
                  <div className="text-xs text-gray-400 mt-1">до {expiryDate.toLocaleDateString('ru-RU')}</div>
                </div>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-6 mb-6">
                <label className="block text-lg font-bold text-white mb-4">Срок выкупа: {optionDays} дней</label>
                <input
                  type="range" min="7" max="30" value={optionDays}
                  onChange={(e) => setOptionDays(Number(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
                <div className="flex justify-between text-sm text-gray-400 mt-2">
                  <span>7 дней</span><span>30 дней</span>
                </div>
                <div className="mt-4 text-center">
                  <div className="text-gray-400">Переплата</div>
                  <div className="text-xl font-bold text-orange-400">{formatMoney(overpayment)} ₽</div>
                </div>
              </div>
              
              <button onClick={() => setStep('kyc')}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-4 rounded-lg transition">
                Продолжить →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: KYC */}
        {step === 'kyc' && (
          <div className="space-y-6">
            <h1 className="text-4xl font-bold text-white">Верификация</h1>
            
            <div className="bg-[#0f1419] border border-gray-800 rounded-xl p-6">
              <div className="mb-6">
                <label className="block text-sm font-medium text-white mb-2">📱 Номер телефона</label>
                <input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)}
                  placeholder="+7 999 123-45-67"
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-blue-500 focus:outline-none" />
              </div>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-white mb-2">📷 Фото паспорта (разворот с фото)</label>
                <input type="file" ref={fileInputRef} accept="image/*" onChange={handlePassportUpload} className="hidden" />
                {passportPhoto ? (
                  <div className="relative">
                    <img src={passportPhoto} alt="Паспорт" className="w-full max-h-60 object-contain rounded-lg border border-gray-700" />
                    <button onClick={() => { setPassportPhoto(null); setPassportData(null); }} className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full">✕</button>
                    <div className="mt-2 text-sm text-green-400">✓ Фото загружено. Заполните данные ниже.</div>
                  </div>
                ) : (
                  <button onClick={() => fileInputRef.current?.click()}
                    className="w-full border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-blue-500 hover:bg-gray-800/50 transition">
                    <div className="text-4xl mb-2">📷</div>
                    <div className="text-white font-medium">Загрузить фото</div>
                    <div className="text-gray-400 text-sm">Разворот с фотографией</div>
                  </button>
                )}
              </div>
              
              {/* Ручной ввод данных паспорта */}
              {passportPhoto && (
                <div className="mb-6 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                  <h3 className="text-white font-medium mb-4">📝 Данные паспорта</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">ФИО *</label>
                      <input 
                        type="text" 
                        value={passportData?.full_name || ''} 
                        onChange={(e) => setPassportData(prev => prev ? {...prev, full_name: e.target.value} : {full_name: e.target.value, series: '', number: '', birth_date: '', issue_date: '', department_code: '', gender: '', confidence: 1, surname: '', name: '', patronymic: '', birth_place: '', raw_text: ''})}
                        placeholder="Иванов Иван Иванович"
                        className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Серия</label>
                        <input 
                          type="text" 
                          value={passportData?.series || ''} 
                          onChange={(e) => setPassportData(prev => prev ? {...prev, series: e.target.value} : {full_name: '', series: e.target.value, number: '', birth_date: '', issue_date: '', department_code: '', gender: '', confidence: 1, surname: '', name: '', patronymic: '', birth_place: '', raw_text: ''})}
                          placeholder="29 20"
                          className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Номер</label>
                        <input 
                          type="text" 
                          value={passportData?.number || ''} 
                          onChange={(e) => setPassportData(prev => prev ? {...prev, number: e.target.value} : {full_name: '', series: '', number: e.target.value, birth_date: '', issue_date: '', department_code: '', gender: '', confidence: 1, surname: '', name: '', patronymic: '', birth_place: '', raw_text: ''})}
                          placeholder="000000"
                          className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Дата рождения</label>
                      <input 
                        type="text" 
                        value={passportData?.birth_date || ''} 
                        onChange={(e) => setPassportData(prev => prev ? {...prev, birth_date: e.target.value} : {full_name: '', series: '', number: '', birth_date: e.target.value, issue_date: '', department_code: '', gender: '', confidence: 1, surname: '', name: '', patronymic: '', birth_place: '', raw_text: ''})}
                        placeholder="01.01.1990"
                        className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">Код подразделения</label>
                      <input 
                        type="text" 
                        value={passportData?.department_code || ''} 
                        onChange={(e) => setPassportData(prev => prev ? {...prev, department_code: e.target.value} : {full_name: '', series: '', number: '', birth_date: '', issue_date: '', department_code: e.target.value, gender: '', confidence: 1, surname: '', name: '', patronymic: '', birth_place: '', raw_text: ''})}
                        placeholder="292-000"
                        className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>
                </div>
              )}
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-white mb-2">🏠 Фото прописки (страница регистрации)</label>
                <input type="file" ref={registrationInputRef} accept="image/*" onChange={handleRegistrationUpload} className="hidden" />
                {registrationPhoto ? (
                  <div className="relative">
                    <img src={registrationPhoto} alt="Прописка" className="w-full max-h-60 object-contain rounded-lg border border-gray-700" />
                    <button onClick={() => setRegistrationPhoto(null)} className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full">✕</button>
                    <div className="mt-2 text-sm text-green-400">✓ Фото загружено</div>
                  </div>
                ) : (
                  <button onClick={() => registrationInputRef.current?.click()}
                    className="w-full border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-blue-500 hover:bg-gray-800/50 transition">
                    <div className="text-4xl mb-2">🏠</div>
                    <div className="text-white font-medium">Загрузить фото</div>
                    <div className="text-gray-400 text-sm">Страница с пропиской</div>
                  </button>
                )}
              </div>
              
              {/* Поле для адреса прописки */}
              {registrationPhoto && (
                <div className="mb-6 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                  <h3 className="text-white font-medium mb-4">📍 Адрес регистрации</h3>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Адрес прописки *</label>
                    <input 
                      type="text" 
                      value={registrationAddress} 
                      onChange={(e) => setRegistrationAddress(e.target.value)}
                      placeholder="г. Москва, ул. Примерная, д. 1, кв. 1"
                      className="w-full bg-gray-900 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                </div>
              )}
              
              <button onClick={confirmKyc} disabled={!passportPhoto || !registrationPhoto}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 text-white font-bold py-4 rounded-lg transition">
                Продолжить →
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Договор */}
        {step === 'sign' && (
          <div className="space-y-6">
            <h1 className="text-4xl font-bold text-white">Договор</h1>
            
            <div className="bg-[#0f1419] border border-gray-800 rounded-xl p-6">
              {/* Профессиональный договор */}
              <div className="bg-white text-black rounded-lg p-8 mb-6 max-h-[700px] overflow-y-auto text-[12px] leading-[1.6] font-['Times_New_Roman',_serif]" style={{fontFamily: "'Times New Roman', Times, serif"}}>
                
                {/* Шапка */}
                <div className="text-center mb-6">
                  <p className="text-[10px] text-gray-500 mb-4">Экземпляр Продавца</p>
                  <h1 className="text-xl font-bold tracking-wide">ДОГОВОР № {contractNumber}</h1>
                  <h2 className="text-base mt-1">купли-продажи цифровых прав (имущественных прав)</h2>
                  <h3 className="text-sm text-gray-600">с опционом на обратный выкуп</h3>
                </div>
                
                <div className="flex justify-between text-sm mb-6">
                  <span>г. Москва</span>
                  <span>«{new Date().getDate()}» {new Date().toLocaleString('ru-RU', { month: 'long' })} {new Date().getFullYear()} г.</span>
                </div>
                
                {/* Преамбула */}
                <p className="mb-3 text-justify">
                  <strong>Общество с ограниченной ответственностью «КиберЛомбард»</strong> (ООО «КиберЛомбард»), 
                  ИНН 7700000000, ОГРН 1234567890123, юридический адрес: 123456, г. Москва, ул. Примерная, д. 1, 
                  в лице Генерального директора Иванова Ивана Ивановича, действующего на основании Устава, 
                  именуемое в дальнейшем <strong>«Покупатель»</strong>, с одной стороны, и
                </p>
                <p className="mb-3 text-justify">
                  {passportData?.full_name ? (
                    <>Гражданин(ка) Российской Федерации <strong>{passportData.full_name}</strong>, 
                    паспорт серия <strong>{passportData.series}</strong> № <strong>{passportData.number}</strong>
                    {passportData.birth_date && <>, дата рождения: {passportData.birth_date}</>}
                    {passportData.issue_date && <>, выдан: {passportData.issue_date}</>}
                    {passportData.department_code && <>, код подразделения: {passportData.department_code}</>}, </>
                  ) : (
                    <>Физическое лицо, идентифицированное посредством загруженных документов, удостоверяющих личность 
                    (паспорт гражданина Российской Федерации), </>
                  )}
                  контактный телефон: <strong>{phone || '+7 (XXX) XXX-XX-XX'}</strong>, 
                  именуемое в дальнейшем <strong>«Продавец»</strong>, с другой стороны,
                </p>
                <p className="mb-4 text-justify">
                  совместно именуемые <strong>«Стороны»</strong>, а по отдельности — <strong>«Сторона»</strong>, 
                  руководствуясь принципом свободы договора (статья 421 Гражданского кодекса Российской Федерации), 
                  заключили настоящий Договор (далее — «Договор») о нижеследующем:
                </p>

                {/* Раздел 1 */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">1. ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ</h3>
                  <p className="mb-1 text-justify"><strong>1.1.</strong> <em>Цифровые права</em> — в соответствии со статьёй 141.1 Гражданского кодекса Российской Федерации, обязательственные и иные права, содержание и условия осуществления которых определяются в соответствии с правилами информационной системы.</p>
                  <p className="mb-1 text-justify"><strong>1.2.</strong> <em>Внутриигровые предметы (скины)</em> — цифровые объекты, представляющие собой лицензионный контент компьютерной игры Counter-Strike 2, принадлежащей Valve Corporation, функционирующие в рамках платформы Steam.</p>
                  <p className="mb-1 text-justify"><strong>1.3.</strong> <em>Платформа Steam</em> — цифровая платформа дистрибуции компьютерных игр и программного обеспечения, принадлежащая Valve Corporation (США).</p>
                  <p className="mb-1 text-justify"><strong>1.4.</strong> <em>Опцион на обратный выкуп</em> — право (но не обязанность) Продавца выкупить переданные Покупателю цифровые права в течение установленного срока по заранее определённой цене.</p>
                  <p className="mb-1 text-justify"><strong>1.5.</strong> <em>Trade Offer (Предложение обмена)</em> — функционал платформы Steam, позволяющий осуществлять передачу внутриигровых предметов между пользователями.</p>
                </div>
                
                {/* Раздел 2 */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">2. ПРЕДМЕТ ДОГОВОРА</h3>
                  <p className="mb-1 text-justify"><strong>2.1.</strong> Продавец обязуется передать в собственность Покупателя, а Покупатель обязуется принять и оплатить цифровые права на внутриигровые предметы (скины) компьютерной игры Counter-Strike 2 (далее — «Предметы»).</p>
                  <p className="mb-1 text-justify"><strong>2.2.</strong> Перечень передаваемых Предметов (Приложение № 1):</p>
                  
                  {/* Таблица скинов */}
                  <table className="w-full border-collapse text-[11px] my-2">
                    <thead>
                      <tr className="bg-gray-100">
                        <th className="border border-gray-300 px-1 py-1 text-left">№</th>
                        <th className="border border-gray-300 px-1 py-1 text-left">Наименование</th>
                        <th className="border border-gray-300 px-1 py-1 text-center">Качество</th>
                        <th className="border border-gray-300 px-1 py-1 text-center">Редкость</th>
                        <th className="border border-gray-300 px-1 py-1 text-right">Сумма, ₽</th>
                      </tr>
                    </thead>
                    <tbody>
                      {quote?.items?.slice(0, 10).map((item: any, idx: number) => (
                        <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                          <td className="border border-gray-300 px-1 py-0.5">{idx + 1}</td>
                          <td className="border border-gray-300 px-1 py-0.5 truncate max-w-[200px]" title={item.market_hash_name || item.name}>
                            {(item.market_hash_name || item.name || 'Unknown').substring(0, 40)}
                            {(item.market_hash_name || item.name || '').length > 40 ? '...' : ''}
                          </td>
                          <td className="border border-gray-300 px-1 py-0.5 text-center text-[10px]">
                            {item.exterior || item.wear_name || '—'}
                          </td>
                          <td className="border border-gray-300 px-1 py-0.5 text-center text-[10px]">
                            {item.rarity || item.quality || '—'}
                          </td>
                          <td className="border border-gray-300 px-1 py-0.5 text-right">
                            {formatMoney(item.loan_price || (item.market_price || item.instant_price || 0) * 0.40)}
                          </td>
                        </tr>
                      ))}
                      {(quote?.items?.length || 0) > 10 && (
                        <tr className="bg-gray-100">
                          <td colSpan={4} className="border border-gray-300 px-1 py-0.5 text-center italic">
                            ... и ещё {(quote?.items?.length || 0) - 10} предметов
                          </td>
                          <td className="border border-gray-300 px-1 py-0.5 text-right font-bold">
                            {formatMoney(quote?.items?.slice(10).reduce((sum: number, i: any) => sum + (i.loan_price || (i.market_price || i.instant_price || 0) * 0.40), 0))}
                          </td>
                        </tr>
                      )}
                      <tr className="bg-gray-200 font-bold">
                        <td colSpan={4} className="border border-gray-300 px-1 py-1 text-right">ИТОГО ({quote?.items?.length || 0} шт.):</td>
                        <td className="border border-gray-300 px-1 py-1 text-right">{formatMoney(loanAmount)}</td>
                      </tr>
                    </tbody>
                  </table>
                  
                  <p className="mb-1 text-justify"><strong>2.3.</strong> Одновременно с передачей права собственности на Предметы Покупатель предоставляет Продавцу опцион (право) на обратный выкуп Предметов на условиях, определённых разделом 5 настоящего Договора.</p>
                  <p className="mb-1 text-justify"><strong>2.4.</strong> Право собственности на Предметы переходит к Покупателю с момента фактического получения Предметов посредством функции Trade Offer платформы Steam.</p>
                </div>

                {/* Раздел 3 */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">3. ЦЕНА ДОГОВОРА И ПОРЯДОК РАСЧЁТОВ</h3>
                  <p className="mb-1 text-justify"><strong>3.1.</strong> Цена Договора (сумма, подлежащая выплате Продавцу за передаваемые Предметы) составляет: <strong>{formatMoney(loanAmount)} ({loanAmount > 0 ? 'прописью' : 'ноль'}) рублей 00 копеек</strong>, в том числе НДС не облагается на основании применения специального налогового режима.</p>
                  <p className="mb-1 text-justify"><strong>3.2.</strong> Оплата производится Покупателем в течение 24 (двадцати четырёх) часов с момента подтверждения получения Предметов следующим способом:</p>
                  <p className="mb-1 ml-4">— перевод денежных средств через Систему быстрых платежей (СБП) Банка России; или</p>
                  <p className="mb-1 ml-4">— перевод на банковскую карту Продавца.</p>
                  <p className="mb-1 text-justify"><strong>3.3.</strong> Обязательство Покупателя по оплате считается исполненным с момента списания денежных средств с расчётного счёта Покупателя.</p>
                </div>
                
                {/* Раздел 4 */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">4. ПОРЯДОК ПЕРЕДАЧИ ПРЕДМЕТОВ</h3>
                  <p className="mb-1 text-justify"><strong>4.1.</strong> Передача Предметов осуществляется исключительно посредством функции Trade Offer (Предложение обмена) платформы Steam.</p>
                  <p className="mb-1 text-justify"><strong>4.2.</strong> Продавец обязуется направить Покупателю предложение обмена (Trade Offer), содержащее все Предметы, указанные в Приложении № 1, в течение 24 (двадцати четырёх) часов с момента подписания настоящего Договора.</p>
                  <p className="mb-1 text-justify"><strong>4.3.</strong> Покупатель обязуется принять предложение обмена в течение 48 (сорока восьми) часов с момента его получения.</p>
                  <p className="mb-1 text-justify"><strong>4.4.</strong> Моментом передачи Предметов считается момент успешного завершения обмена на платформе Steam, подтверждённый соответствующим уведомлением системы.</p>
                  <p className="mb-1 text-justify"><strong>4.5.</strong> В случае невозможности передачи Предметов по техническим причинам (блокировка обмена, ограничения Steam Guard и т.п.) Стороны обязуются уведомить друг друга и согласовать новый срок передачи.</p>
                </div>

                {/* Раздел 5 */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">5. ОПЦИОН НА ОБРАТНЫЙ ВЫКУП</h3>
                  <p className="mb-1 text-justify"><strong>5.1.</strong> Покупатель предоставляет Продавцу безотзывный опцион (право) на обратный выкуп Предметов на следующих условиях:</p>
                  <p className="mb-1 ml-4"><strong>5.1.1.</strong> Срок действия опциона: <strong>{optionDays} ({optionDays} прописью) календарных дней</strong> с момента подписания настоящего Договора.</p>
                  <p className="mb-1 ml-4"><strong>5.1.2.</strong> Дата окончания срока опциона: <strong>{formatDate(expiryDate)}</strong>, 23:59:59 по московскому времени.</p>
                  <p className="mb-1 ml-4"><strong>5.1.3.</strong> Цена обратного выкупа (цена исполнения опциона): <strong>{formatMoney(buybackPrice)} рублей</strong>.</p>
                  <p className="mb-1 text-justify"><strong>5.2.</strong> Цена обратного выкупа включает:</p>
                  <p className="mb-1 ml-4">— сумму, выплаченную Продавцу по п. 3.1: {formatMoney(loanAmount)} руб.;</p>
                  <p className="mb-1 ml-4">— вознаграждение за предоставление опциона ({(interestRate.total * 100).toFixed(1)}%): {formatMoney(overpayment)} руб.</p>
                  <p className="mb-1 text-justify"><strong>5.3.</strong> Для реализации права на обратный выкуп Продавец обязан:</p>
                  <p className="mb-1 ml-4">а) уведомить Покупателя о намерении воспользоваться опционом;</p>
                  <p className="mb-1 ml-4">б) произвести оплату цены обратного выкупа в полном объёме до истечения срока опциона.</p>
                  <p className="mb-1 text-justify"><strong>5.4.</strong> Покупатель обязуется передать Предметы обратно Продавцу в течение 24 (двадцати четырёх) часов с момента получения полной оплаты цены обратного выкупа.</p>
                  <p className="mb-1 text-justify"><strong>5.5.</strong> По истечении срока действия опциона (п. 5.1.2) право Продавца на обратный выкуп прекращается автоматически без какого-либо дополнительного уведомления. Предметы остаются в собственности Покупателя без каких-либо компенсаций Продавцу.</p>
                </div>

                {/* Раздел 6 */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">6. ЗАВЕРЕНИЯ И ГАРАНТИИ</h3>
                  <p className="mb-1 text-justify"><strong>6.1.</strong> Продавец заверяет и гарантирует, что:</p>
                  <p className="mb-1 ml-4">а) является законным владельцем передаваемых Предметов;</p>
                  <p className="mb-1 ml-4">б) Предметы не обременены правами третьих лиц, не находятся в споре или под арестом;</p>
                  <p className="mb-1 ml-4">в) аккаунт Steam, с которого осуществляется передача, принадлежит Продавцу и не имеет ограничений на обмен;</p>
                  <p className="mb-1 ml-4">г) Предметы получены законным путём и не являются результатом мошеннических действий.</p>
                  <p className="mb-1 text-justify"><strong>6.2.</strong> Покупатель заверяет и гарантирует, что:</p>
                  <p className="mb-1 ml-4">а) обладает необходимыми полномочиями для заключения настоящего Договора;</p>
                  <p className="mb-1 ml-4">б) располагает достаточными денежными средствами для исполнения обязательств по Договору.</p>
                </div>
                
                {/* Раздел 7 - УСИЛЕННАЯ ЗАЩИТА РИСКОВ */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">7. РИСКИ, ОГРАНИЧЕНИЯ И ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ</h3>
                  
                  <p className="mb-1 text-justify"><strong>7.1. Природа цифровых активов.</strong> Стороны осознают и безоговорочно принимают, что:</p>
                  <p className="mb-1 ml-4">7.1.1. Предметы Договора являются виртуальными объектами, существующими исключительно в рамках программного обеспечения Valve Corporation, и не имеют материального воплощения;</p>
                  <p className="mb-1 ml-4">7.1.2. Предметы представляют собой лицензионный контент, права на который принадлежат Valve Corporation, и могут быть в любой момент заблокированы, удалены, изменены, обесценены или полностью ликвидированы по единоличному решению правообладателя без какого-либо предварительного уведомления и без компенсации;</p>
                  <p className="mb-1 ml-4">7.1.3. Valve Corporation вправе в одностороннем порядке изменять правила платформы Steam, включая полный запрет на обмен предметами;</p>
                  <p className="mb-1 ml-4">7.1.4. Рыночная стоимость Предметов крайне волатильна и может измениться на 100% в любую сторону в течение нескольких часов.</p>
                  
                  <p className="mb-1 text-justify"><strong>7.2. Распределение рисков.</strong> Продавец принимает на себя следующие риски:</p>
                  <p className="mb-1 ml-4">7.2.1. Риск блокировки аккаунта Steam Продавца по любым основаниям (VAC-бан, Trade Ban, нарушение правил Steam);</p>
                  <p className="mb-1 ml-4">7.2.2. Риск отмены, отката или аннулирования обмена по инициативе Steam, третьих лиц или в результате мошеннических действий;</p>
                  <p className="mb-1 ml-4">7.2.3. Риск признания Предметов украденными, полученными мошенническим путём или обременёнными правами третьих лиц;</p>
                  <p className="mb-1 ml-4">7.2.4. Риск технических сбоев, потери доступа к аккаунту, взлома аккаунта Продавца;</p>
                  <p className="mb-1 ml-4">7.2.5. Риск изменения законодательства, влияющего на оборот цифровых активов.</p>
                  
                  <p className="mb-1 text-justify"><strong>7.3. Полный отказ от ответственности Покупателя.</strong> Покупатель не несёт никакой ответственности за:</p>
                  <p className="mb-1 ml-4">7.3.1. Любые действия или бездействие Valve Corporation, включая блокировку Предметов, аккаунтов, изменение правил;</p>
                  <p className="mb-1 ml-4">7.3.2. Снижение рыночной стоимости Предметов после заключения Договора;</p>
                  <p className="mb-1 ml-4">7.3.3. Невозможность обратного выкупа по причинам, не зависящим от Покупателя;</p>
                  <p className="mb-1 ml-4">7.3.4. Действия третьих лиц, включая хакерские атаки, мошенничество, претензии правообладателей;</p>
                  <p className="mb-1 ml-4">7.3.5. Любые убытки Продавца, возникшие в связи с исполнением настоящего Договора.</p>
                  
                  <p className="mb-1 text-justify"><strong>7.4. Правовая квалификация.</strong> Настоящий Договор НЕ является:</p>
                  <p className="mb-1 ml-4">— договором займа или кредита (глава 42 ГК РФ);</p>
                  <p className="mb-1 ml-4">— договором залога (§ 3 главы 23 ГК РФ);</p>
                  <p className="mb-1 ml-4">— ломбардной операцией (Федеральный закон № 196-ФЗ);</p>
                  <p className="mb-1 ml-4">— финансовой услугой в смысле законодательства о защите прав потребителей.</p>
                  <p className="mb-1 text-justify">Отношения Сторон регулируются исключительно нормами о купле-продаже (глава 30 ГК РФ) и опционном договоре (статья 429.2 ГК РФ).</p>
                  
                  <p className="mb-1 text-justify"><strong>7.5.</strong> Продавец подтверждает, что осознаёт все вышеуказанные риски, принимает их добровольно и отказывается от любых претензий к Покупателю, связанных с реализацией данных рисков.</p>
                </div>

                {/* Раздел 8 - УСИЛЕННАЯ ОТВЕТСТВЕННОСТЬ */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">8. ОТВЕТСТВЕННОСТЬ СТОРОН И САНКЦИИ</h3>
                  
                  <p className="mb-1 text-justify"><strong>8.1. Ответственность Продавца.</strong></p>
                  <p className="mb-1 ml-4">8.1.1. В случае отмены, отката обмена или возврата Предметов по любым основаниям после получения оплаты, Продавец обязуется в течение 3 (трёх) календарных дней возвратить полученную сумму в полном объёме с уплатой штрафа в размере 30% (тридцати процентов) от суммы Договора;</p>
                  <p className="mb-1 ml-4">8.1.2. В случае выявления факта мошенничества, предоставления заведомо ложных сведений или передачи Предметов, полученных преступным путём, Продавец обязуется возместить все убытки Покупателя, включая упущенную выгоду, а также уплатить штраф в размере 100% (ста процентов) от суммы Договора;</p>
                  <p className="mb-1 ml-4">8.1.3. Продавец несёт ответственность за достоверность предоставленных персональных данных и документов;</p>
                  <p className="mb-1 ml-4">8.1.4. При просрочке возврата денежных средств начисляется пеня в размере 1% (одного процента) от суммы задолженности за каждый день просрочки.</p>
                  
                  <p className="mb-1 text-justify"><strong>8.2. Ограничение ответственности Покупателя.</strong></p>
                  <p className="mb-1 ml-4">8.2.1. Максимальная ответственность Покупателя по настоящему Договору ограничена суммой, фактически полученной от Продавца;</p>
                  <p className="mb-1 ml-4">8.2.2. Покупатель не несёт ответственности за косвенные убытки, упущенную выгоду, моральный вред Продавца;</p>
                  <p className="mb-1 ml-4">8.2.3. Покупатель освобождается от ответственности при наступлении обстоятельств непреодолимой силы.</p>
                  
                  <p className="mb-1 text-justify"><strong>8.3. Неосновательное обогащение.</strong> В соответствии со статьёй 1102 ГК РФ, в случае получения Продавцом денежных средств без встречного предоставления (передачи Предметов), такие средства подлежат возврату как неосновательное обогащение с начислением процентов по статье 395 ГК РФ.</p>
                  
                  <p className="mb-1 text-justify"><strong>8.4. Право на взыскание.</strong> Покупатель вправе обратиться в суд и/или правоохранительные органы для защиты своих прав, а также передать право требования третьим лицам (коллекторским агентствам) без согласия Продавца.</p>
                </div>
                
                {/* Раздел 9 */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">9. ПОРЯДОК РАЗРЕШЕНИЯ СПОРОВ</h3>
                  <p className="mb-1 text-justify"><strong>9.1.</strong> Все споры и разногласия, возникающие из настоящего Договора или в связи с ним, Стороны будут стремиться разрешить путём переговоров.</p>
                  <p className="mb-1 text-justify"><strong>9.2.</strong> Претензионный порядок урегулирования споров является обязательным. Срок рассмотрения претензии — 10 (десять) рабочих дней с момента её получения.</p>
                  <p className="mb-1 text-justify"><strong>9.3.</strong> При недостижении согласия споры подлежат рассмотрению в суде по месту нахождения Покупателя в соответствии с законодательством Российской Федерации.</p>
                </div>

                {/* Раздел 10 */}
                <div className="mb-4">
                  <h3 className="font-bold text-sm border-b border-gray-300 pb-1 mb-2">10. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ</h3>
                  <p className="mb-1 text-justify"><strong>10.1.</strong> Настоящий Договор вступает в силу с момента его подписания обеими Сторонами и действует до полного исполнения Сторонами своих обязательств.</p>
                  <p className="mb-1 text-justify"><strong>10.2.</strong> Договор составлен в электронной форме. В соответствии со статьёй 6 Федерального закона от 06.04.2011 № 63-ФЗ «Об электронной подписи» и статьёй 160 ГК РФ, Стороны признают юридическую силу документов, подписанных простой электронной подписью.</p>
                  <p className="mb-1 text-justify"><strong>10.3.</strong> Простой электронной подписью Продавца признаётся совокупность следующих данных: номер мобильного телефона, подтверждённый посредством SMS-кода, и/или авторизация через аккаунт Steam.</p>
                  <p className="mb-1 text-justify"><strong>10.4.</strong> Все изменения и дополнения к настоящему Договору действительны при условии их совершения в письменной форме (в том числе электронной) и подписания обеими Сторонами.</p>
                  <p className="mb-1 text-justify"><strong>10.5.</strong> Во всём, что не предусмотрено настоящим Договором, Стороны руководствуются действующим законодательством Российской Федерации.</p>
                  <p className="mb-1 text-justify"><strong>10.6.</strong> Приложения к настоящему Договору являются его неотъемлемой частью:</p>
                  <p className="mb-1 ml-4">— Приложение № 1: Перечень передаваемых Предметов.</p>
                </div>
                
                {/* Раздел 11 - Реквизиты */}
                <div className="border-t-2 border-gray-400 pt-4 mt-6">
                  <h3 className="font-bold text-sm mb-4 text-center">11. АДРЕСА, РЕКВИЗИТЫ И ПОДПИСИ СТОРОН</h3>
                  <div className="grid grid-cols-2 gap-8 text-xs">
                    <div className="border-r border-gray-300 pr-4">
                      <p className="font-bold mb-2">ПОКУПАТЕЛЬ:</p>
                      <p className="mb-1">ООО «КиберЛомбард»</p>
                      <p className="mb-1">ИНН 7700000000 / КПП 770001001</p>
                      <p className="mb-1">ОГРН 1234567890123</p>
                      <p className="mb-1">Адрес: 123456, г. Москва,</p>
                      <p className="mb-1">ул. Примерная, д. 1</p>
                      <p className="mb-1">Р/с 40702810000000000000</p>
                      <p className="mb-1">в ПАО «Сбербанк»</p>
                      <p className="mb-1">БИК 044525225</p>
                      <p className="mb-3">К/с 30101810400000000225</p>
                      <p className="mb-1">Генеральный директор</p>
                      <p className="border-b border-gray-400 mb-1 pb-4"></p>
                      <p className="text-center">_________________ / Иванов И.И. /</p>
                      <p className="text-center text-gray-500 text-[10px]">М.П.</p>
                    </div>
                    <div className="pl-4">
                      <p className="font-bold mb-2">ПРОДАВЕЦ:</p>
                      <p className="mb-1">{passportData?.full_name || 'Физическое лицо'}</p>
                      <p className="mb-1">Телефон: {phone || '+7 (XXX) XXX-XX-XX'}</p>
                      {passportData ? (
                        <>
                          <p className="mb-1">Паспорт: {passportData.series} {passportData.number}</p>
                          {passportData.birth_date && <p className="mb-1">Дата рожд.: {passportData.birth_date}</p>}
                          {passportData.issue_date && <p className="mb-1">Выдан: {passportData.issue_date}</p>}
                          {passportData.department_code && <p className="mb-1">Код: {passportData.department_code}</p>}
                        </>
                      ) : (
                        <>
                          <p className="mb-1">Паспорт: данные согласно</p>
                          <p className="mb-1">загруженным документам</p>
                        </>
                      )}
                      <p className="mb-1">&nbsp;</p>
                      <p className="mb-3">&nbsp;</p>
                      <p className="border-b border-gray-400 mb-1 pb-4"></p>
                      <p className="text-center">_________________ / {passportData?.full_name?.split(' ').map(n => n[0]).join('.') || 'ФИО'}. /</p>
                      <p className="text-center text-gray-500 text-[10px]">Подпись Продавца</p>
                    </div>
                  </div>
                </div>

                {/* Электронная подпись */}
                <div className="mt-6 p-4 bg-gray-100 rounded text-xs">
                  <p className="font-bold mb-2">СВЕДЕНИЯ ОБ ЭЛЕКТРОННОЙ ПОДПИСИ:</p>
                  <p>Дата и время подписания: {new Date().toLocaleString('ru-RU')} (МСК)</p>
                  <p>Способ идентификации: загрузка документа, удостоверяющего личность{passportData ? ' (OCR распознавание)' : ''}</p>
                  {passportData?.full_name && <p>ФИО: {passportData.full_name}</p>}
                  <p>Контактный телефон: {phone || 'не указан'}</p>
                  <p>Идентификатор сессии: {contractNumber}</p>
                  <p className="mt-2 text-gray-500">
                    Подписывая настоящий Договор, Продавец подтверждает, что ознакомлен с его условиями, 
                    понимает правовую природу сделки и связанные с ней риски, действует добровольно и в своём интересе.
                  </p>
                </div>
                
              </div>
              
              {/* Чекбокс согласия */}
              <div className="mb-6">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input type="checkbox" checked={acceptTerms} onChange={(e) => setAcceptTerms(e.target.checked)} className="mt-1 w-5 h-5" />
                  <span className="text-sm text-gray-300">
                    Я, Продавец, подтверждаю, что полностью ознакомлен с условиями настоящего Договора, 
                    понимаю правовую природу сделки (купля-продажа с опционом на обратный выкуп), осознаю 
                    связанные с ней риски, в том числе риск утраты права на обратный выкуп по истечении 
                    установленного срока. Подтверждаю, что действую добровольно, в своём интересе и без 
                    принуждения (статья 421 ГК РФ — свобода договора).
                  </span>
                </label>
              </div>
              
              {/* Кнопка подписания */}
              <button onClick={createDeal} disabled={!acceptTerms || dealCreating}
                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 text-white font-bold py-4 rounded-lg transition flex items-center justify-center gap-2">
                {dealCreating ? (
                  <><div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>Создание сделки...</>
                ) : (
                  <>✍️ Подписать договор простой электронной подписью</>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
