<script setup lang="ts">
import { GitCompareArrows, Trash2 } from '@lucide/vue'
import { useStorefrontStore } from '@/stores/storefront'
const storefront = useStorefrontStore()
</script>

<template>
  <div v-if="storefront.compareIds.length" class="compare-tray" aria-live="polite">
    <div>
      <GitCompareArrows :size="20" /><span
        >已选 {{ storefront.compareIds.length }}/3：{{ storefront.compareIds.join('、') }}</span
      >
    </div>
    <p v-if="storefront.compareError">{{ storefront.compareError }}</p>
    <div class="compare-actions">
      <button type="button" class="clear" aria-label="清空对比" @click="storefront.clearCompare">
        <Trash2 :size="17" />
      </button>
      <button
        type="button"
        :disabled="storefront.compareIds.length < 2 || storefront.compareLoading"
        @click="storefront.runComparison"
      >
        {{ storefront.compareLoading ? '比较中…' : '开始比较' }}
      </button>
    </div>
  </div>
</template>
