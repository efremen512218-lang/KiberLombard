const SteamUser = require('steam-user');
const SteamTotp = require('steam-totp');
const TradeOfferManager = require('steam-tradeoffer-manager');
const SteamCommunity = require('steamcommunity');
const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

// Steam клиенты
const client = new SteamUser();
const community = new SteamCommunity();
const manager = new TradeOfferManager({
  steam: client,
  community: community,
  language: 'ru'
});

// Конфигурация
const config = {
  username: process.env.STEAM_USERNAME,
  password: process.env.STEAM_PASSWORD,
  sharedSecret: process.env.STEAM_SHARED_SECRET,
  identitySecret: process.env.IDENTITY_SECRET,
  apiUrl: process.env.API_URL || 'http://localhost:8000',
  port: process.env.PORT || 3001
};

// Логин в Steam
const loginOptions = {
  accountName: config.username,
  password: config.password,
  twoFactorCode: SteamTotp.generateAuthCode(config.sharedSecret)
};

console.log('[BOT] Подключение к Steam...');
client.logOn(loginOptions);

// События Steam
client.on('loggedOn', () => {
  console.log('[BOT] ✅ Успешный вход в Steam');
  client.setPersona(SteamUser.EPersonaState.Online);
  client.gamesPlayed([730]); // CS2
});

client.on('webSession', (sessionid, cookies) => {
  console.log('[BOT] ✅ Web сессия получена');
  manager.setCookies(cookies);
  community.setCookies(cookies);
});

client.on('error', (err) => {
  console.error('[BOT] ❌ Ошибка Steam:', err);
});

// Обработка входящих трейдов
manager.on('newOffer', async (offer) => {
  console.log(`[BOT] 📨 Новый трейд #${offer.id} от ${offer.partner.getSteamID64()}`);
  
  try {
    // Проверяем, это наш ожидаемый трейд?
    const response = await axios.get(`${config.apiUrl}/api/trades/verify/${offer.id}`);
    
    if (response.data.valid) {
      // Принимаем трейд
      offer.accept((err, status) => {
        if (err) {
          console.error(`[BOT] ❌ Ошибка принятия трейда:`, err);
          return;
        }
        
        console.log(`[BOT] ✅ Трейд #${offer.id} принят. Статус: ${status}`);
        
        // Подтверждаем через мобильный аутентификатор
        if (status === 'pending') {
          community.acceptConfirmationForObject(config.identitySecret, offer.id, (err) => {
            if (err) {
              console.error(`[BOT] ❌ Ошибка подтверждения:`, err);
            } else {
              console.log(`[BOT] ✅ Трейд #${offer.id} подтвержден`);
              
              // Уведомляем backend
              notifyBackend(offer.id, 'ACCEPTED', response.data.deal_id);
            }
          });
        }
      });
    } else {
      console.log(`[BOT] ⚠️ Трейд #${offer.id} не найден в системе, отклоняем`);
      offer.decline();
    }
  } catch (error) {
    console.error(`[BOT] ❌ Ошибка проверки трейда:`, error.message);
    offer.decline();
  }
});

manager.on('sentOfferChanged', (offer, oldState) => {
  console.log(`[BOT] 📤 Статус отправленного трейда #${offer.id} изменен: ${TradeOfferManager.ETradeOfferState[oldState]} → ${TradeOfferManager.ETradeOfferState[offer.state]}`);
  
  if (offer.state === TradeOfferManager.ETradeOfferState.Accepted) {
    console.log(`[BOT] ✅ Трейд #${offer.id} принят получателем`);
  }
});

// API endpoints
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    steam_connected: client.steamID !== null,
    timestamp: new Date().toISOString()
  });
});

// Создать трейд-оффер (получение скинов от клиента)
app.post('/api/trade/create', async (req, res) => {
  const { deal_id, partner_steam_id, items } = req.body;
  
  try {
    const offer = manager.createOffer(partner_steam_id);
    
    // Запрашиваем предметы у клиента
    items.forEach(item => {
      offer.addTheirItem({
        appid: 730,
        contextid: 2,
        assetid: item.assetid
      });
    });
    
    offer.setMessage(`КиберЛомбард CS2 - Сделка #${deal_id}. Выкуп скинов.`);
    
    offer.send((err, status) => {
      if (err) {
        console.error('[BOT] ❌ Ошибка отправки трейда:', err);
        return res.status(500).json({ error: err.message });
      }
      
      console.log(`[BOT] ✅ Трейд #${offer.id} отправлен. Статус: ${status}`);
      
      res.json({
        success: true,
        trade_offer_id: offer.id,
        trade_url: `https://steamcommunity.com/tradeoffer/${offer.id}/`,
        status: status
      });
    });
  } catch (error) {
    console.error('[BOT] ❌ Ошибка создания трейда:', error);
    res.status(500).json({ error: error.message });
  }
});

// Создать обратный трейд (возврат скинов клиенту)
app.post('/api/trade/reverse', async (req, res) => {
  const { deal_id, partner_steam_id, items } = req.body;
  
  try {
    const offer = manager.createOffer(partner_steam_id);
    
    // Отдаем предметы клиенту (эквивалентные или те же)
    items.forEach(item => {
      offer.addMyItem({
        appid: 730,
        contextid: 2,
        assetid: item.assetid
      });
    });
    
    offer.setMessage(`КиберЛомбард CS2 - Сделка #${deal_id}. Обратный выкуп.`);
    
    offer.send((err, status) => {
      if (err) {
        console.error('[BOT] ❌ Ошибка отправки обратного трейда:', err);
        return res.status(500).json({ error: err.message });
      }
      
      console.log(`[BOT] ✅ Обратный трейд #${offer.id} отправлен`);
      
      // Автоподтверждение
      if (status === 'pending') {
        community.acceptConfirmationForObject(config.identitySecret, offer.id, (err) => {
          if (err) {
            console.error('[BOT] ❌ Ошибка подтверждения:', err);
          }
        });
      }
      
      res.json({
        success: true,
        trade_offer_id: offer.id,
        trade_url: `https://steamcommunity.com/tradeoffer/${offer.id}/`,
        status: status
      });
    });
  } catch (error) {
    console.error('[BOT] ❌ Ошибка создания обратного трейда:', error);
    res.status(500).json({ error: error.message });
  }
});

// Получить инвентарь бота
app.get('/api/inventory', (req, res) => {
  manager.getInventoryContents(730, 2, true, (err, inventory) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    
    res.json({
      items: inventory.map(item => ({
        assetid: item.assetid,
        market_hash_name: item.market_hash_name,
        name: item.name,
        type: item.type
      }))
    });
  });
});

// Получить инвентарь любого пользователя по Steam ID
app.get('/api/inventory/:steamid', (req, res) => {
  const { steamid } = req.params;
  
  console.log(`[BOT] Загрузка инвентаря для ${steamid}`);
  
  manager.getUserInventoryContents(steamid, 730, 2, true, (err, inventory, currencies) => {
    if (err) {
      console.error(`[BOT] Ошибка загрузки инвентаря: ${err.message}`);
      return res.status(500).json({ 
        error: err.message,
        details: 'Возможно инвентарь приватный или аккаунт ограничен'
      });
    }
    
    console.log(`[BOT] Загружено ${inventory.length} предметов`);
    
    const items = inventory.map(item => ({
      assetid: item.assetid,
      classid: item.classid,
      instanceid: item.instanceid,
      market_hash_name: item.market_hash_name,
      name: item.name,
      type: item.type,
      icon_url: `https://community.cloudflare.steamstatic.com/economy/image/${item.icon_url}`,
      tradable: item.tradable,
      marketable: item.marketable,
      amount: item.amount
    }));
    
    // Фильтруем только tradable предметы
    const tradableItems = items.filter(item => item.tradable);
    
    res.json({
      success: true,
      steam_id: steamid,
      total_items: items.length,
      tradable_items: tradableItems.length,
      items: tradableItems
    });
  });
});

// Проверить статус трейда
app.get('/api/trade/status/:tradeOfferId', (req, res) => {
  const { tradeOfferId } = req.params;
  
  manager.getOffer(tradeOfferId, (err, offer) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    
    const statusMap = {
      1: 'INVALID',
      2: 'ACTIVE',
      3: 'ACCEPTED',
      4: 'COUNTERED',
      5: 'EXPIRED',
      6: 'CANCELED',
      7: 'DECLINED',
      8: 'INVALID_ITEMS',
      9: 'NEEDS_CONFIRMATION',
      10: 'CANCELED_BY_SECOND_FACTOR',
      11: 'IN_ESCROW'
    };
    
    res.json({
      trade_offer_id: offer.id,
      status: statusMap[offer.state] || 'UNKNOWN',
      state_code: offer.state,
      created: offer.created,
      updated: offer.updated,
      expires: offer.expires
    });
  });
});

// Уведомить backend об изменении статуса трейда
async function notifyBackend(tradeOfferId, status, dealId) {
  try {
    await axios.post(`${config.apiUrl}/api/trades/${tradeOfferId}/status`, {
      status: status,
      deal_id: dealId
    });
    console.log(`[BOT] ✅ Backend уведомлен о трейде #${tradeOfferId}`);
  } catch (error) {
    console.error(`[BOT] ❌ Ошибка уведомления backend:`, error.message);
  }
}

// Запуск сервера
app.listen(config.port, () => {
  console.log(`[BOT] 🚀 API запущен на порту ${config.port}`);
});
