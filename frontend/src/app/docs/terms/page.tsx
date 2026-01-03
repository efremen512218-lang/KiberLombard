'use client'

import Link from 'next/link'

export default function TermsPage() {
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

      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8 neon-text">Пользовательское соглашение</h1>
        
        <div className="cyber-card space-y-6 text-gray-300">
          <section>
            <h2 className="text-2xl font-bold text-white mb-4">1. Общие положения</h2>
            <p className="mb-4">
              1.1. Настоящее Пользовательское соглашение (далее — «Соглашение») регулирует отношения между 
              ООО «КиберЛомбард» (далее — «Сервис») и пользователем (далее — «Пользователь») при использовании 
              веб-сайта и сервисов КиберЛомбард CS2.
            </p>
            <p className="mb-4">
              1.2. Используя сервис, Пользователь подтверждает, что ознакомился с настоящим Соглашением и 
              принимает все его условия в полном объеме.
            </p>
            <p>
              1.3. Если Пользователь не согласен с условиями Соглашения, он обязан прекратить использование сервиса.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">2. Предмет соглашения</h2>
            <p className="mb-4">
              2.1. Сервис предоставляет Пользователю возможность выкупа цифровых прав на внутриигровые предметы 
              Counter-Strike 2 (далее — «Предметы») с опционом обратного выкупа.
            </p>
            <p className="mb-4">
              2.2. <strong className="text-red-400">Сервис НЕ является ломбардом</strong> и не осуществляет 
              ломбардную деятельность. Правовая модель основана на договоре купли-продажи с опционом обратного 
              выкупа (ст. 454, 429.3 ГК РФ).
            </p>
            <p>
              2.3. Предметы CS2 являются лицензионным контентом Valve Corporation и не являются вещами в 
              понимании гражданского законодательства РФ.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">3. Порядок использования сервиса</h2>
            <p className="mb-4">
              3.1. Для использования сервиса Пользователь должен:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Пройти авторизацию через Steam OpenID</li>
              <li>Подтвердить номер телефона через SMS</li>
              <li>Предоставить паспортные данные (для сумм более 15,000₽)</li>
              <li>Подписать договор выкупа с использованием ПЭП</li>
            </ul>
            <p className="mb-4">
              3.2. Пользователь выбирает Предметы из своего инвентаря CS2 для выкупа.
            </p>
            <p className="mb-4">
              3.3. Сервис рассчитывает условия сделки:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Сумма выплаты: 65% от средней рыночной цены</li>
              <li>Цена выкупа: 115% от рыночной + премия опциона 25%</li>
              <li>Срок опциона: от 7 до 30 дней (выбирает Пользователь)</li>
            </ul>
            <p>
              3.4. После подписания договора Пользователь передает Предметы через Steam Trade Offer и 
              получает выплату на банковскую карту.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">4. Опцион обратного выкупа</h2>
            <p className="mb-4">
              4.1. Пользователь имеет право выкупить Предметы обратно в течение срока опциона по 
              фиксированной цене, указанной в договоре.
            </p>
            <p className="mb-4">
              4.2. Для реализации опциона Пользователь обязан:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Оплатить сумму выкупа в полном объеме</li>
              <li>Подтвердить операцию SMS-кодом</li>
              <li>Принять обратный Trade Offer в течение 48 часов</li>
            </ul>
            <p className="mb-4">
              4.3. <strong className="text-red-400">После истечения срока опциона возврат Предметов и/или 
              денежных средств НЕВОЗМОЖЕН.</strong> Предметы переходят в полное распоряжение Сервиса.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">5. Риски и ответственность</h2>
            <p className="mb-4">
              5.1. Пользователь полностью осознает и принимает следующие риски:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Предметы могут быть заблокированы/удалены Valve без компенсации</li>
              <li>VAC-бан аккаунта может привести к блокировке трейдов</li>
              <li>Steam может откатить трейд в случае мошенничества/взлома</li>
              <li>Valve может изменить условия использования Предметов</li>
            </ul>
            <p className="mb-4">
              5.2. В случае отката трейда по инициативе Steam, Пользователь обязан вернуть Сервису 
              полученную сумму + 20% в течение 3 дней (ст. 1102 ГК РФ — неосновательное обогащение).
            </p>
            <p>
              5.3. Сервис не несет ответственности за действия Valve Corporation, блокировки аккаунтов, 
              изменения в игре или любые другие обстоятельства, связанные с функционированием Steam и CS2.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">6. Персональные данные</h2>
            <p className="mb-4">
              6.1. Сервис обрабатывает персональные данные Пользователя в соответствии с 
              Федеральным законом №152-ФЗ «О персональных данных».
            </p>
            <p className="mb-4">
              6.2. Обрабатываемые данные:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Steam ID и профиль</li>
              <li>Номер телефона</li>
              <li>Паспортные данные (для сумм более 15,000₽)</li>
              <li>Данные о сделках и трейдах</li>
            </ul>
            <p>
              6.3. Подробнее о обработке персональных данных см. в Политике конфиденциальности.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">7. Разрешение споров</h2>
            <p className="mb-4">
              7.1. Все споры разрешаются путем переговоров. Претензионный порядок обязателен.
            </p>
            <p className="mb-4">
              7.2. Срок ответа на претензию — 10 рабочих дней.
            </p>
            <p>
              7.3. При недостижении согласия споры разрешаются в судах г. Москвы по законодательству РФ.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">8. Заключительные положения</h2>
            <p className="mb-4">
              8.1. Сервис вправе изменять условия настоящего Соглашения в одностороннем порядке.
            </p>
            <p className="mb-4">
              8.2. Новая редакция Соглашения вступает в силу с момента ее размещения на сайте.
            </p>
            <p>
              8.3. Продолжение использования сервиса после изменения Соглашения означает принятие 
              новых условий.
            </p>
          </section>

          <div className="border-t border-gray-700 pt-6 mt-8">
            <p className="text-sm text-gray-400">
              Дата последнего обновления: 05.12.2025
            </p>
            <p className="text-sm text-gray-400 mt-2">
              ООО «КиберЛомбард»<br />
              ИНН: 1234567890<br />
              ОГРН: 1234567890123<br />
              Email: legal@cyberlombard.ru
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
