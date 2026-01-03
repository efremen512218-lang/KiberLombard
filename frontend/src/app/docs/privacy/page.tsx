'use client'

import Link from 'next/link'

export default function PrivacyPage() {
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
        <h1 className="text-4xl font-bold mb-8 neon-text">Политика конфиденциальности</h1>
        
        <div className="cyber-card space-y-6 text-gray-300">
          <section>
            <h2 className="text-2xl font-bold text-white mb-4">1. Общие положения</h2>
            <p className="mb-4">
              1.1. Настоящая Политика конфиденциальности (далее — «Политика») определяет порядок обработки 
              и защиты персональных данных пользователей сервиса КиберЛомбард CS2.
            </p>
            <p className="mb-4">
              1.2. Обработка персональных данных осуществляется в соответствии с:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Федеральным законом №152-ФЗ «О персональных данных»</li>
              <li>Федеральным законом №115-ФЗ «О противодействии легализации доходов»</li>
              <li>Другими нормативными актами РФ</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">2. Какие данные мы собираем</h2>
            <p className="mb-4">
              2.1. <strong className="text-white">Данные Steam:</strong>
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Steam ID (уникальный идентификатор)</li>
              <li>Имя профиля Steam</li>
              <li>Аватар профиля</li>
              <li>URL профиля</li>
              <li>Данные инвентаря CS2</li>
            </ul>
            
            <p className="mb-4">
              2.2. <strong className="text-white">Контактные данные:</strong>
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Номер телефона (для SMS-верификации)</li>
              <li>Email (опционально)</li>
            </ul>
            
            <p className="mb-4">
              2.3. <strong className="text-white">Паспортные данные (для сумм более 15,000₽):</strong>
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Серия и номер паспорта</li>
              <li>Кем и когда выдан</li>
              <li>Код подразделения</li>
              <li>Фото разворота паспорта (для сумм более 100,000₽)</li>
            </ul>
            
            <p className="mb-4">
              2.4. <strong className="text-white">Данные о сделках:</strong>
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Информация о выкупленных предметах</li>
              <li>Суммы сделок</li>
              <li>Даты и время операций</li>
              <li>Trade ID и статусы трейдов</li>
              <li>Платежные данные (без реквизитов карт)</li>
            </ul>
            
            <p className="mb-4">
              2.5. <strong className="text-white">Технические данные:</strong>
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>IP-адрес</li>
              <li>User Agent (браузер и ОС)</li>
              <li>Cookies</li>
              <li>Логи действий в системе</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">3. Цели обработки данных</h2>
            <p className="mb-4">
              3.1. Мы обрабатываем персональные данные для:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Идентификации пользователя</li>
              <li>Заключения и исполнения договоров</li>
              <li>Соблюдения требований 115-ФЗ (ПОД/ФТ)</li>
              <li>Предотвращения мошенничества</li>
              <li>Связи с пользователем</li>
              <li>Улучшения качества сервиса</li>
              <li>Выполнения обязательств перед регуляторами</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">4. Правовые основания обработки</h2>
            <p className="mb-4">
              4.1. Обработка персональных данных осуществляется на основании:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Согласия пользователя (ст. 9 ФЗ-152)</li>
              <li>Необходимости исполнения договора (ст. 6 ФЗ-152)</li>
              <li>Требований законодательства (115-ФЗ, 152-ФЗ)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">5. Защита данных</h2>
            <p className="mb-4">
              5.1. Мы применяем следующие меры защиты:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Шифрование данных (SSL/TLS, AES-256)</li>
              <li>Хеширование паролей и SMS-кодов (SHA-256)</li>
              <li>Ограничение доступа к данным</li>
              <li>Регулярные аудиты безопасности</li>
              <li>Резервное копирование</li>
              <li>Мониторинг подозрительной активности</li>
            </ul>
            
            <p className="mb-4">
              5.2. Паспортные данные хранятся в зашифрованном виде на защищенных серверах.
            </p>
            
            <p>
              5.3. SMS-коды не хранятся в открытом виде, только хеши.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">6. Передача данных третьим лицам</h2>
            <p className="mb-4">
              6.1. Мы можем передавать данные следующим категориям лиц:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li><strong>Платежные системы:</strong> ЮKassa, СБП (для выплат)</li>
              <li><strong>SMS-провайдеры:</strong> SMS.ru (для отправки кодов)</li>
              <li><strong>Государственные органы:</strong> по запросу (Росфинмониторинг, суды)</li>
            </ul>
            
            <p>
              6.2. Мы НЕ продаем и не передаем данные третьим лицам для маркетинговых целей.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">7. Срок хранения данных</h2>
            <p className="mb-4">
              7.1. Сроки хранения:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li><strong>Паспортные данные:</strong> 5 лет после последней сделки (115-ФЗ)</li>
              <li><strong>Данные о сделках:</strong> 5 лет (115-ФЗ)</li>
              <li><strong>SMS-коды (хеши):</strong> 5 лет</li>
              <li><strong>Логи действий:</strong> 1 год</li>
              <li><strong>Технические данные:</strong> 6 месяцев</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">8. Права пользователя</h2>
            <p className="mb-4">
              8.1. Вы имеете право:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Получить информацию о обрабатываемых данных</li>
              <li>Требовать уточнения или удаления данных</li>
              <li>Отозвать согласие на обработку</li>
              <li>Обжаловать действия в Роскомнадзоре</li>
            </ul>
            
            <p className="mb-4">
              8.2. Для реализации прав обращайтесь: privacy@cyberlombard.ru
            </p>
            
            <p>
              8.3. <strong className="text-yellow-400">Важно:</strong> Удаление данных невозможно в течение 
              5 лет после сделки (требование 115-ФЗ).
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">9. Cookies</h2>
            <p className="mb-4">
              9.1. Мы используем cookies для:
            </p>
            <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
              <li>Авторизации пользователя</li>
              <li>Сохранения настроек</li>
              <li>Аналитики (анонимно)</li>
            </ul>
            
            <p>
              9.2. Вы можете отключить cookies в настройках браузера, но это может ограничить функциональность.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">10. Изменения в Политике</h2>
            <p className="mb-4">
              10.1. Мы вправе изменять Политику в одностороннем порядке.
            </p>
            <p>
              10.2. Новая редакция вступает в силу с момента размещения на сайте.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-white mb-4">11. Контакты</h2>
            <p className="mb-4">
              По вопросам обработки персональных данных:
            </p>
            <ul className="space-y-2">
              <li><strong>Email:</strong> privacy@cyberlombard.ru</li>
              <li><strong>Телефон:</strong> +7 (495) 123-45-67</li>
              <li><strong>Адрес:</strong> г. Москва, ул. Примерная, д. 1</li>
            </ul>
          </section>

          <div className="border-t border-gray-700 pt-6 mt-8">
            <p className="text-sm text-gray-400">
              Дата последнего обновления: 05.12.2025
            </p>
            <p className="text-sm text-gray-400 mt-2">
              ООО «КиберЛомбард»<br />
              ИНН: 1234567890<br />
              ОГРН: 1234567890123
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
