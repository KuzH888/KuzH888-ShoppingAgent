import type { ChatResponse, ModelsResponse, ProductsResponse } from '@/types/api'

const API_PREFIX = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null
    throw new Error(payload?.detail ?? `Request failed with status ${response.status}`)
  }
  return (await response.json()) as T
}

export const api = {
  getModels: () => request<ModelsResponse>(`${API_PREFIX}/models`),
  getProducts: () => request<ProductsResponse>(`${API_PREFIX}/products`),
  sendMessage: (sessionId: string, message: string, modelId: string) =>
    request<ChatResponse>(`${API_PREFIX}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message, model_id: modelId }),
    }),
  resetSession: (sessionId: string) =>
    request<{ session_id: string; reset: true }>(`${API_PREFIX}/sessions/${sessionId}`, {
      method: 'DELETE',
    }),
}
