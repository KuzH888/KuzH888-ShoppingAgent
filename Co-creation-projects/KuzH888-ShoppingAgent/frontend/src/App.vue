<script setup lang="ts">
import { ArrowRight, Bot, ShieldCheck, SlidersHorizontal } from '@lucide/vue'
import { onMounted, onUnmounted } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import ChatWidget from '@/components/ChatWidget.vue'
import CompareTray from '@/components/CompareTray.vue'
import ComparisonModal from '@/components/ComparisonModal.vue'
import ProductDetailDrawer from '@/components/ProductDetailDrawer.vue'
import ProductCard from '@/components/ProductCard.vue'
import { useChatStore } from '@/stores/chat'
import { useStorefrontStore, type CategoryFilter } from '@/stores/storefront'
import { registerStorefrontTools } from '@/webmcp'

const storefront = useStorefrontStore()
const chat = useChatStore()

const categories: Array<{ id: CategoryFilter; label: string }> = [
  { id: 'all', label: '全部商品' },
  { id: 'digital_accessories', label: '数码配件' },
  { id: 'home_office', label: '居家办公' },
  { id: 'travel_lifestyle', label: '旅行生活' },
]

let unregisterTools: () => void = () => {}

onMounted(() => {
  void storefront.loadStorefront()
  unregisterTools = registerStorefrontTools({
    filterCategory: (category) => {
      storefront.selectedCategory = category
      document.querySelector('#catalogue')?.scrollIntoView({ behavior: 'smooth' })
    },
    openAssistant: () => chat.openWithPrompt(),
  })
})

onUnmounted(() => unregisterTools())
</script>

<template>
  <div class="app-shell">
    <AppHeader />

    <main>
      <section class="hero" aria-labelledby="hero-title">
        <img
          src="/kuzmall-lifestyle.png"
          alt="耳机、键盘、台灯、背包与水瓶组成的生活方式商品组合"
        />
        <div class="hero-overlay"></div>
        <div class="hero-copy">
          <span class="eyebrow"><Bot :size="16" /> AI 辅助选品</span>
          <h1 id="hero-title">少一点选择困难，<br /><em>多一点真正合适。</em></h1>
          <p>告诉 KuzBot 你的预算、场景和在意的功能，从 24 件精选好物中找到答案。</p>
          <button type="button" @click="chat.openWithPrompt()">
            让客服帮我选 <ArrowRight :size="18" />
          </button>
        </div>
        <div class="hero-proof">
          <span><ShieldCheck :size="18" /> 真实目录数据</span>
          <span><SlidersHorizontal :size="18" /> 可解释匹配</span>
        </div>
      </section>

      <section id="catalogue" class="catalogue-section" aria-labelledby="catalogue-title">
        <div class="section-heading">
          <div>
            <span class="section-kicker">KuzMall 精选</span>
            <h2 id="catalogue-title">为日常挑一件好物</h2>
          </div>
          <p>价格、库存和功能均来自本地商品目录，智能客服不会编造商品信息。</p>
        </div>

        <nav class="category-tabs" aria-label="商品分类">
          <button
            v-for="category in categories"
            :key="category.id"
            type="button"
            :class="{ active: storefront.selectedCategory === category.id }"
            @click="storefront.selectedCategory = category.id"
          >
            {{ category.label }}
          </button>
        </nav>

        <div v-if="storefront.loading" class="status-panel">正在载入商品目录…</div>
        <div v-else-if="storefront.error" class="status-panel error">
          <strong>暂时无法读取商品</strong>
          <span>{{ storefront.error }}</span>
          <button type="button" @click="storefront.loadStorefront">重新加载</button>
        </div>
        <div v-else class="product-grid">
          <ProductCard
            v-for="product in storefront.visibleProducts"
            :key="product.id"
            :product="product"
          />
        </div>
      </section>
    </main>

    <footer>
      <a class="brand footer-brand" href="#catalogue">Kuz<span>Mall</span></a>
      <p>智能推荐仅基于当前模拟商品目录。</p>
      <span>Graduation Project · 2026</span>
    </footer>

    <ChatWidget />
    <CompareTray />
    <ProductDetailDrawer />
    <ComparisonModal />
  </div>
</template>
