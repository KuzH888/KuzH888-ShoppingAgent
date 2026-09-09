import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { api } from '@/api/client'
import type { Category, Product, PublicModel } from '@/types/api'

export type CategoryFilter = 'all' | Category

export const useStorefrontStore = defineStore('storefront', () => {
  const products = ref<Product[]>([])
  const models = ref<PublicModel[]>([])
  const selectedModel = ref('')
  const selectedCategory = ref<CategoryFilter>('all')
  const loading = ref(false)
  const error = ref('')

  const visibleProducts = computed(() =>
    selectedCategory.value === 'all'
      ? products.value
      : products.value.filter((product) => product.category === selectedCategory.value),
  )

  async function loadStorefront() {
    loading.value = true
    error.value = ''
    try {
      const [productData, modelData] = await Promise.all([api.getProducts(), api.getModels()])
      products.value = productData.products
      models.value = modelData.models
      selectedModel.value = modelData.default_model
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : '商城数据加载失败'
    } finally {
      loading.value = false
    }
  }

  return {
    products,
    models,
    selectedModel,
    selectedCategory,
    loading,
    error,
    visibleProducts,
    loadStorefront,
  }
})
