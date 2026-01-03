'use client'

import { useEffect, useState } from 'react'

export default function TestInventoryPage() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [steamId, setSteamId] = useState<string>('')

  useEffect(() => {
    const id = localStorage.getItem('steam_id') || '76561198000000000'
    setSteamId(id)
    const apiUrl = 'http://localhost:8000'
    
    console.log('Fetching inventory...')
    console.log('Steam ID:', id)
    console.log('API URL:', apiUrl)
    
    fetch(`${apiUrl}/api/inventory/${id}`)
      .then(res => {
        console.log('Response status:', res.status)
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`)
        }
        return res.json()
      })
      .then(data => {
        console.log('Data received:', data)
        setData(data)
      })
      .catch(err => {
        console.error('Error:', err)
        setError(err.message)
      })
  }, [])

  return (
    <div className="min-h-screen p-8 bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-4">Test Inventory</h1>
      
      <div className="mb-4">
        <strong>Steam ID:</strong> {steamId || 'Not set'}
      </div>
      
      {error && (
        <div className="bg-red-900 p-4 rounded mb-4">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {data && (
        <div className="bg-gray-800 p-4 rounded">
          <h2 className="text-xl font-bold mb-2">Data:</h2>
          <pre className="text-xs overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
      
      {!data && !error && (
        <div>Loading...</div>
      )}
    </div>
  )
}
