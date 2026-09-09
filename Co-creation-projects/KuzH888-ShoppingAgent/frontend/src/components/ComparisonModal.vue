<script setup lang="ts">
import { MessageCircle, X } from '@lucide/vue'
import { useChatStore } from '@/stores/chat'
import { useStorefrontStore } from '@/stores/storefront'

const storefront = useStorefrontStore()
const chat = useChatStore()

function askAssistant() {
  const ids = storefront.comparison.map((product) => product.product_id)
  storefront.compareOpen = false
  chat.openWithPrompt(`请比较 ${ids.join(' 和 ')}，说明主要差异。`)
}
</script>

<template>
  <div
    v-if="storefront.compareOpen"
    class="modal-backdrop comparison-backdrop"
    @click.self="storefront.compareOpen = false"
  >
    <section
      class="comparison-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="comparison-title"
    >
      <header>
        <div>
          <small>FACT-BASED COMPARISON</small>
          <h2 id="comparison-title">商品对比</h2>
        </div>
        <button type="button" aria-label="关闭商品对比" @click="storefront.compareOpen = false">
          <X :size="21" />
        </button>
      </header>
      <div class="comparison-grid" :style="{ '--columns': storefront.comparison.length }">
        <article v-for="product in storefront.comparison" :key="product.product_id">
          <small>{{ product.product_id }}</small>
          <h3>{{ product.name }}</h3>
          <strong>{{ product.currency }} {{ product.price.toFixed(2) }}</strong>
          <dl>
            <dt>评分</dt>
            <dd>{{ product.rating }}/5</dd>
            <dt>库存</dt>
            <dd>{{ product.stock }} 件</dd>
            <dt>保修</dt>
            <dd>{{ product.warranty_months }} 个月</dd>
            <dt>主要功能</dt>
            <dd>{{ product.features.slice(0, 5).join('、').replaceAll('_', ' ') }}</dd>
          </dl>
        </article>
      </div>
      <button class="primary-action comparison-ask" type="button" @click="askAssistant">
        <MessageCircle :size="18" />让客服解释如何选择
      </button>
    </section>
  </div>
</template>
