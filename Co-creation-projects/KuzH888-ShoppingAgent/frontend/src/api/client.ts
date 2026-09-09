import type {
  ChatResponse,
  ComparisonProduct,
  ModelsResponse,
  Product,
  ProductsResponse,
  StorePolicy,
} from '@/types/api'

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
  getProduct: (productId: string) => request<Product>(`${API_PREFIX}/products/${productId}`),
  compareProducts: (productIds: string[]) =>
    request<{ products: ComparisonProduct[] }>(`${API_PREFIX}/products/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_ids: productIds, language: 'zh' }),
    }),
  getPolicies: () => request<{ policies: StorePolicy[] }>(`${API_PREFIX}/policies`),
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
