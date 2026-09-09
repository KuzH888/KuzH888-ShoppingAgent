import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '@/api/client'
import { useStorefrontStore } from '@/stores/storefront'

vi.mock('@/api/client', () => ({
  api: { compareProducts: vi.fn() },
}))

describe('storefront comparison', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('limits selection to three unique products and supports removal', () => {
    const store = useStorefrontStore()
    ;['DIG-001', 'DIG-002', 'DIG-003', 'DIG-004'].forEach(store.toggleCompare)
    expect(store.compareIds).toEqual(['DIG-001', 'DIG-002', 'DIG-003'])
    store.toggleCompare('DIG-002')
    expect(store.compareIds).toEqual(['DIG-001', 'DIG-003'])
  })

  it('opens comparison after the backend returns facts', async () => {
    vi.mocked(api.compareProducts).mockResolvedValue({
      products: [
        {
          product_id: 'DIG-001',
          name: 'A',
          price: 10,
          currency: 'AUD',
          stock: 1,
          rating: 4.5,
          features: [],
          use_cases: [],
          warranty_months: 12,
          specifications: {},
        },
        {
          product_id: 'DIG-003',
          name: 'B',
          price: 20,
          currency: 'AUD',
          stock: 2,
          rating: 4.2,
          features: [],
          use_cases: [],
          warranty_months: 12,
          specifications: {},
        },
      ],
    })
    const store = useStorefrontStore()
    store.compareIds = ['DIG-001', 'DIG-003']
    await store.runComparison()
    expect(store.compareOpen).toBe(true)
    expect(store.comparison).toHaveLength(2)
  })
})
