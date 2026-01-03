'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'

export default function ContractPage() {
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

  const formatMoney = (value: number) => {
    return (value || 0).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-xl text-black">Загрузка договора...</div>
      </div>
    )
  }

  if (!deal) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-xl text-black">Договор не найден</div>
      </div>
    )
  }

  const contractNumber = `КЛ-${new Date(deal.created_at).getFullYear()}-${String(deal.id).padStart(6, '0')}`
  const createdDate = new Date(deal.created_at)
  const expiryDate = new Date(deal.option_expiry)
  
  // Расчёт процентов
  const overpayment = (deal.buyback_price || 0) - (deal.loan_amount || 0)
  const interestPercent = deal.loan_amount > 0 ? ((overpayment / deal.loan_amount) * 100).toFixed(1) : '0'

  return (
    <div className="min-h-screen bg-white p-8 print:p-4" style={{fontFamily: "'Times New Roman', Times, serif"}}>
      <div className="max-w-4xl mx-auto text-black text-[13px] leading-relaxed">
        
        {/* Кнопка печати */}
        <div className="print:hidden mb-4 flex gap-4">
          <button onClick={() => window.print()} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
            🖨️ Печать / Сохранить PDF
          </button>
          <button onClick={() => window.close()} className="bg-gray-600 text-white px-6 py-2 rounded hover:bg-gray-700">
            ✕ Закрыть
          </button>
        </div>

        {/* Шапка */}
        <div className="text-center mb-8">
          <p className="text-[10px] text-gray-500 mb-4">Экземпляр Продавца</p>
          <h1 className="text-2xl font-bold tracking-wide">ДОГОВОР № {contractNumber}</h1>
          <h2 className="text-lg mt-2">купли-продажи цифровых прав (имущественных прав)</h2>
          <h3 className="text-base text-gray-600">с опционом на обратный выкуп</h3>
        </div>
        
        <div className="flex justify-between mb-8">
          <span>г. Москва</span>
          <span>«{createdDate.getDate()}» {createdDate.toLocaleString('ru-RU', { month: 'long' })} {createdDate.getFullYear()} г.</span>
        </div>
        
        {/* Преамбула */}
        <p className="mb-4 text-justify">
          <strong>Общество с ограниченной ответственностью «КиберЛомбард»</strong> (ООО «КиберЛомбард»), 
          ИНН 7700000000, ОГРН 1234567890123, юридический адрес: 123456, г. Москва, ул. Примерная, д. 1, 
          в лице Генерального директора Иванова Ивана Ивановича, действующего на основании Устава, 
          именуемое в дальнейшем <strong>«Покупатель»</strong>, с одной стороны, и
        </p>
        <p className="mb-4 text-justify">
          {deal.kyc_snapshot?.full_name ? (
            <>
              Гражданин(ка) Российской Федерации <strong>{deal.kyc_snapshot.full_name}</strong>, 
              паспорт серия <strong>{deal.kyc_snapshot.passport_series}</strong> № <strong>{deal.kyc_snapshot.passport_number}</strong>
              {deal.kyc_snapshot.birth_date && <>, дата рождения: {deal.kyc_snapshot.birth_date}</>}
              {deal.kyc_snapshot.department_code && <>, код подразделения: {deal.kyc_snapshot.department_code}</>}
              {deal.kyc_snapshot.registration_address && <>, зарегистрированный(ая) по адресу: {deal.kyc_snapshot.registration_address}</>}
              {deal.kyc_snapshot.phone && <>, контактный телефон: {deal.kyc_snapshot.phone}</>}
              , Steam ID: <strong>{deal.kyc_snapshot.steam_id || deal.user?.steam_id}</strong>
              {deal.kyc_snapshot.steam_username && <> (никнейм: {deal.kyc_snapshot.steam_username})</>}
            </>
          ) : (
            <>
              Физическое лицо, идентифицированное посредством Steam ID: <strong>{deal.user?.steam_id || 'N/A'}</strong>
              {deal.user?.steam_username && <> (никнейм: {deal.user.steam_username})</>}
            </>
          )}, 
          именуемое в дальнейшем <strong>«Продавец»</strong>, с другой стороны,
        </p>
        <p className="mb-6 text-justify">
          совместно именуемые <strong>«Стороны»</strong>, а по отдельности — <strong>«Сторона»</strong>, 
          руководствуясь принципом свободы договора (статья 421 Гражданского кодекса Российской Федерации), 
          заключили настоящий Договор (далее — «Договор») о нижеследующем:
        </p>

        {/* Раздел 1 - Термины */}
        <div className="mb-6">
          <h3 className="font-bold border-b-2 border-black pb-1 mb-3">1. ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ</h3>
          <p className="mb-2 text-justify"><strong>1.1.</strong> <em>Цифровые права</em> — в соответствии со статьёй 141.1 ГК РФ, обязательственные и иные права, содержание и условия осуществления которых определяются в соответствии с правилами информационной системы.</p>
          <p className="mb-2 text-justify"><strong>1.2.</strong> <em>Внутриигровые предметы (скины)</em> — цифровые объекты, представляющие собой лицензионный контент компьютерной игры Counter-Strike 2, принадлежащей Valve Corporation.</p>
          <p className="mb-2 text-justify"><strong>1.3.</strong> <em>Опцион на обратный выкуп</em> — право (но не обязанность) Продавца выкупить переданные Покупателю цифровые права в течение установленного срока по заранее определённой цене.</p>
        </div>
        
        {/* Раздел 2 - Предмет */}
        <div className="mb-6">
          <h3 className="font-bold border-b-2 border-black pb-1 mb-3">2. ПРЕДМЕТ ДОГОВОРА</h3>
          <p className="mb-3 text-justify"><strong>2.1.</strong> Продавец обязуется передать в собственность Покупателя, а Покупатель обязуется принять и оплатить цифровые права на внутриигровые предметы (скины) компьютерной игры Counter-Strike 2.</p>
          <p className="mb-3"><strong>2.2.</strong> Перечень передаваемых Предметов:</p>
          
          {/* Таблица скинов */}
          <table className="w-full border-collapse mb-4">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-400 px-2 py-2 text-left w-12">№</th>
                <th className="border border-gray-400 px-2 py-2 text-left">Наименование предмета</th>
                <th className="border border-gray-400 px-2 py-2 text-right w-32">Сумма выдачи</th>
              </tr>
            </thead>
            <tbody>
              {deal.items_snapshot?.map((item: any, idx: number) => {
                const price = typeof item.market_price === 'object' 
                  ? (item.market_price?.instant_price || item.instant_price || 0) 
                  : (item.market_price || item.instant_price || 0)
                const loan = item.loan_price || (price * 0.40)
                return (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="border border-gray-400 px-2 py-1">{idx + 1}</td>
                    <td className="border border-gray-400 px-2 py-1">{item.market_hash_name || item.name}</td>
                    <td className="border border-gray-400 px-2 py-1 text-right">{formatMoney(loan)} ₽</td>
                  </tr>
                )
              })}
              <tr className="bg-gray-200 font-bold">
                <td colSpan={2} className="border border-gray-400 px-2 py-2 text-right">ИТОГО ({deal.items_snapshot?.length || 0} предметов):</td>
                <td className="border border-gray-400 px-2 py-2 text-right">{formatMoney(deal.loan_amount)} ₽</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Раздел 3 - Цена */}
        <div className="mb-6">
          <h3 className="font-bold border-b-2 border-black pb-1 mb-3">3. ЦЕНА ДОГОВОРА И ПОРЯДОК РАСЧЁТОВ</h3>
          <p className="mb-2 text-justify"><strong>3.1.</strong> Цена Договора (сумма, подлежащая выплате Продавцу): <strong>{formatMoney(deal.loan_amount)} рублей</strong>.</p>
          <p className="mb-2 text-justify"><strong>3.2.</strong> Оплата производится Покупателем в течение 24 часов с момента подтверждения получения Предметов через СБП или банковскую карту.</p>
        </div>

        {/* Раздел 4 - Передача */}
        <div className="mb-6">
          <h3 className="font-bold border-b-2 border-black pb-1 mb-3">4. ПОРЯДОК ПЕРЕДАЧИ ПРЕДМЕТОВ</h3>
          <p className="mb-2 text-justify"><strong>4.1.</strong> Передача Предметов осуществляется посредством функции Trade Offer платформы Steam.</p>
          <p className="mb-2 text-justify"><strong>4.2.</strong> Продавец обязуется направить предложение обмена в течение 24 часов с момента подписания Договора.</p>
          <p className="mb-2 text-justify"><strong>4.3.</strong> Моментом передачи считается успешное завершение обмена на платформе Steam.</p>
        </div>

        {/* Раздел 5 - Опцион */}
        <div className="mb-6">
          <h3 className="font-bold border-b-2 border-black pb-1 mb-3">5. ОПЦИОН НА ОБРАТНЫЙ ВЫКУП</h3>
          <p className="mb-2 text-justify"><strong>5.1.</strong> Покупатель предоставляет Продавцу безотзывный опцион на обратный выкуп:</p>
          <p className="mb-2 ml-6"><strong>5.1.1.</strong> Дата окончания срока опциона: <strong>{expiryDate.toLocaleDateString('ru-RU')}</strong>, 23:59:59 МСК.</p>
          <p className="mb-2 ml-6"><strong>5.1.2.</strong> Цена обратного выкупа: <strong>{formatMoney(deal.buyback_price)} рублей</strong>.</p>
          <p className="mb-2 text-justify"><strong>5.2.</strong> Цена обратного выкупа включает:</p>
          <p className="mb-1 ml-6">— сумму, выплаченную Продавцу: {formatMoney(deal.loan_amount)} руб.;</p>
          <p className="mb-2 ml-6">— вознаграждение за предоставление опциона ({interestPercent}%): {formatMoney(overpayment)} руб.</p>
          <p className="mb-2 text-justify"><strong>5.3.</strong> По истечении срока опциона право на обратный выкуп прекращается автоматически без компенсации.</p>
        </div>

        {/* Раздел 6 - Риски */}
        <div className="mb-6">
          <h3 className="font-bold border-b-2 border-black pb-1 mb-3">6. РИСКИ И ОТВЕТСТВЕННОСТЬ</h3>
          <p className="mb-2 text-justify"><strong>6.1.</strong> Продавец принимает на себя риски:</p>
          <p className="mb-1 ml-6">— блокировки аккаунта Steam;</p>
          <p className="mb-1 ml-6">— изменения правил платформы Valve;</p>
          <p className="mb-1 ml-6">— снижения рыночной стоимости предметов;</p>
          <p className="mb-2 ml-6">— невозможности обратного выкупа по истечении срока.</p>
          <p className="mb-2 text-justify"><strong>6.2.</strong> Покупатель не несёт ответственности за действия Valve Corporation и третьих лиц.</p>
          <p className="mb-2 text-justify"><strong>6.3.</strong> Настоящий Договор НЕ является договором займа, залога или ломбардной операцией.</p>
        </div>

        {/* Раздел 7 - Споры */}
        <div className="mb-6">
          <h3 className="font-bold border-b-2 border-black pb-1 mb-3">7. РАЗРЕШЕНИЕ СПОРОВ</h3>
          <p className="mb-2 text-justify"><strong>7.1.</strong> Претензионный порядок обязателен. Срок рассмотрения претензии — 10 рабочих дней.</p>
          <p className="mb-2 text-justify"><strong>7.2.</strong> Споры рассматриваются в суде по месту нахождения Покупателя.</p>
        </div>

        {/* Раздел 8 - Заключительные */}
        <div className="mb-6">
          <h3 className="font-bold border-b-2 border-black pb-1 mb-3">8. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ</h3>
          <p className="mb-2 text-justify"><strong>8.1.</strong> Договор составлен в электронной форме. Стороны признают юридическую силу документов, подписанных простой электронной подписью (ст. 6 ФЗ № 63-ФЗ, ст. 160 ГК РФ).</p>
          <p className="mb-2 text-justify"><strong>8.2.</strong> Простой электронной подписью Продавца признаётся авторизация через аккаунт Steam.</p>
        </div>

        {/* Подписи */}
        <div className="border-t-2 border-black pt-6 mt-8">
          <h3 className="font-bold text-center mb-6">АДРЕСА, РЕКВИЗИТЫ И ПОДПИСИ СТОРОН</h3>
          <div className="grid grid-cols-2 gap-8">
            <div className="border-r border-gray-300 pr-6">
              <p className="font-bold mb-3">ПОКУПАТЕЛЬ:</p>
              <p className="mb-1">ООО «КиберЛомбард»</p>
              <p className="mb-1">ИНН 7700000000 / КПП 770001001</p>
              <p className="mb-1">ОГРН 1234567890123</p>
              <p className="mb-1">123456, г. Москва, ул. Примерная, д. 1</p>
              <p className="mb-4">Р/с 40702810000000000000 в ПАО «Сбербанк»</p>
              <p className="mb-1">Генеральный директор</p>
              <div className="border-b border-black mt-8 mb-1"></div>
              <p className="text-center text-sm">_________________ / Иванов И.И. /</p>
              <p className="text-center text-gray-500 text-xs">М.П.</p>
            </div>
            <div className="pl-6">
              <p className="font-bold mb-3">ПРОДАВЕЦ:</p>
              {deal.kyc_snapshot?.full_name ? (
                <>
                  <p className="mb-1">{deal.kyc_snapshot.full_name}</p>
                  <p className="mb-1">Паспорт: {deal.kyc_snapshot.passport_series} {deal.kyc_snapshot.passport_number}</p>
                  {deal.kyc_snapshot.birth_date && <p className="mb-1">Дата рождения: {deal.kyc_snapshot.birth_date}</p>}
                  {deal.kyc_snapshot.registration_address && <p className="mb-1">Адрес: {deal.kyc_snapshot.registration_address}</p>}
                  {deal.kyc_snapshot.phone && <p className="mb-1">Телефон: {deal.kyc_snapshot.phone}</p>}
                </>
              ) : (
                <p className="mb-1">Физическое лицо</p>
              )}
              <p className="mb-1">Steam ID: {deal.kyc_snapshot?.steam_id || deal.user?.steam_id || 'N/A'}</p>
              <p className="mb-4">Никнейм: {deal.kyc_snapshot?.steam_username || deal.user?.steam_username || 'N/A'}</p>
              <div className="border-b border-black mt-4 mb-1"></div>
              <p className="text-center text-sm">_________________ / {deal.kyc_snapshot?.full_name?.split(' ').slice(0, 1).join('')}. /</p>
            </div>
          </div>
        </div>

        {/* Электронная подпись */}
        <div className="mt-8 p-4 bg-gray-100 border border-gray-300 rounded">
          <p className="font-bold mb-2">СВЕДЕНИЯ ОБ ЭЛЕКТРОННОЙ ПОДПИСИ:</p>
          <p>Дата и время подписания: {createdDate.toLocaleString('ru-RU')} (МСК)</p>
          <p>Способ идентификации: {deal.kyc_snapshot?.full_name ? 'паспорт гражданина РФ + авторизация Steam' : 'авторизация через Steam OpenID'}</p>
          {deal.kyc_snapshot?.full_name && <p>ФИО: {deal.kyc_snapshot.full_name}</p>}
          {deal.kyc_snapshot?.phone && <p>Телефон: {deal.kyc_snapshot.phone}</p>}
          <p>Steam ID: {deal.kyc_snapshot?.steam_id || deal.user?.steam_id || 'N/A'}</p>
          {(deal.kyc_snapshot?.steam_username || deal.user?.steam_username) && <p>Никнейм Steam: {deal.kyc_snapshot?.steam_username || deal.user?.steam_username}</p>}
          <p>Идентификатор договора: {contractNumber}</p>
          <p className="mt-3 text-gray-600 text-sm">
            Подписывая настоящий Договор, Продавец подтверждает, что ознакомлен с его условиями, 
            понимает правовую природу сделки и связанные с ней риски, действует добровольно и в своём интересе.
          </p>
        </div>

      </div>
    </div>
  )
}
