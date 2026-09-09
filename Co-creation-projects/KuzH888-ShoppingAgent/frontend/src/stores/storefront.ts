import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { api } from '@/api/client'
import type { Category, ComparisonProduct, Product, PublicModel, StorePolicy } from '@/types/api'

export type CategoryFilter = 'all' | Category

export const useStorefrontStore = defineStore('storefront', () => {
  const products = ref<Product[]>([])
  const models = ref<PublicModel[]>([])
  const selectedModel = ref('')
  const selectedCategory = ref<CategoryFilter>('all')
  const loading = ref(false)
  const error = ref('')
  const detailProduct = ref<Product | null>(null)
  const detailOpen = ref(false)
  const compareIds = ref<string[]>([])
  const comparison = ref<ComparisonProduct[]>([])
  const compareOpen = ref(false)
  const compareLoading = ref(false)
  const compareError = ref('')
  const policies = ref<StorePolicy[]>([])

  const visibleProducts = computed(() =>
    selectedCategory.value === 'all'
      ? products.value
      : products.value.filter((product) => product.category === selectedCategory.value),
  )

  async function loadStorefront() {
    loading.value = true
    error.value = ''
    try {
      const [productData, modelData, policyData] = await Promise.all([
        api.getProducts(),
        api.getModels(),
        api.getPolicies(),
      ])
      products.value = productData.products
      models.value = modelData.models
      selectedModel.value = modelData.default_model
      policies.value = policyData.policies
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : '商城数据加载失败'
    } finally {
      loading.value = false
    }
  }

  function openDetails(product: Product) {
    detailProduct.value = product
    detailOpen.value = true
  }

  function toggleCompare(productId: string) {
    if (compareIds.value.includes(productId)) {
      compareIds.value = compareIds.value.filter((id) => id !== productId)
      return
    }
    if (compareIds.value.length < 3) compareIds.value.push(productId)
  }

  function clearCompare() {
    compareIds.value = []
    comparison.value = []
    compareOpen.value = false
  }

  async function runComparison() {
    if (compareIds.value.length < 2) return
    compareLoading.value = true
    compareError.value = ''
    try {
      comparison.value = (await api.compareProducts(compareIds.value)).products
      compareOpen.value = true
    } catch (cause) {
      compareError.value = cause instanceof Error ? cause.message : '商品比较失败'
    } finally {
      compareLoading.value = false
    }
  }

  return {
    products,
    models,
    selectedModel,
    selectedCategory,
    loading,
    error,
    detailProduct,
    detailOpen,
    compareIds,
    comparison,
    compareOpen,
    compareLoading,
    compareError,
    policies,
    visibleProducts,
    loadStorefront,
    openDetails,
    toggleCompare,
    clearCompare,
    runComparison,
  }
})
