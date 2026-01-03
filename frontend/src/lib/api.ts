import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auth
export const authAPI = {
  verifySteam: (steamId: string) => 
    api.post('/api/auth/steam/verify', { steam_id: steamId }),
}

// KYC
export const kycAPI = {
  sendPhoneCode: (phone: string) => 
    api.post('/api/kyc/phone/send-code', { phone }),
  
  verifyPhone: (phone: string, code: string, steamId: string) =>
    api.post('/api/kyc/phone/verify', { phone, code, steam_id: steamId }),
  
  submitPassport: (steamId: string, data: any) =>
    api.post('/api/kyc/passport', { steam_id: steamId, ...data }),
}

// Inventory
export const inventoryAPI = {
  getInventory: (steamId: string) =>
    api.get(`/api/inventory/${steamId}`),
}

// Quotes
export const quoteAPI = {
  calculate: (data: any) =>
    api.post('/api/quote', data),
}

// Deals
export const dealAPI = {
  create: (data: any) =>
    api.post('/api/deals', data),
  
  getAll: (steamId: string) =>
    api.get(`/api/deals?steam_id=${steamId}`),
  
  getOne: (dealId: number) =>
    api.get(`/api/deals/${dealId}`),
  
  accept: (dealId: number) =>
    api.post(`/api/deals/${dealId}/accept`),
  
  buyback: (dealId: number, paymentId: string) =>
    api.post(`/api/deals/${dealId}/buyback`, { payment_id: paymentId }),
}
