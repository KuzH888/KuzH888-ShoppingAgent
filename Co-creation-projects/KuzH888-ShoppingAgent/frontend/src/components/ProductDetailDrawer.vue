<script setup lang="ts">
import { MessageCircle, Star, X } from '@lucide/vue'
import { useChatStore } from '@/stores/chat'
import { useStorefrontStore } from '@/stores/storefront'

const storefront = useStorefrontStore()
const chat = useChatStore()

function askAssistant() {
  const product = storefront.detailProduct
  if (!product) return
  storefront.detailOpen = false
  chat.openWithPrompt(`请介绍 ${product.name.zh}（${product.id}），它适合什么需求？`)
}
</script>

<template>
  <div
    v-if="storefront.detailOpen && storefront.detailProduct"
    class="modal-backdrop"
    @click.self="storefront.detailOpen = false"
  >
    <aside class="detail-drawer" role="dialog" aria-modal="true" aria-labelledby="detail-title">
      <header>
        <div>
          <small>{{ storefront.detailProduct.id }}</small>
          <h2 id="detail-title">{{ storefront.detailProduct.name.zh }}</h2>
        </div>
        <button type="button" aria-label="关闭商品详情" @click="storefront.detailOpen = false">
          <X :size="21" />
        </button>
      </header>
      <p class="detail-description">{{ storefront.detailProduct.description.zh }}</p>
      <div class="detail-stats">
        <strong
          >{{ storefront.detailProduct.currency }}
          {{ storefront.detailProduct.price.toFixed(2) }}</strong
        >
        <span
          ><Star :size="16" fill="currentColor" /> {{ storefront.detailProduct.rating }}（{{
            storefront.detailProduct.review_count
          }}）</span
        >
        <span>{{
          storefront.detailProduct.stock > 0
            ? `现货 ${storefront.detailProduct.stock} 件`
            : '暂时缺货'
        }}</span>
      </div>
      <section>
        <h3>主要功能</h3>
        <div class="detail-chips">
          <span v-for="feature in storefront.detailProduct.features" :key="feature">{{
            feature.replaceAll('_', ' ')
          }}</span>
        </div>
      </section>
      <section>
        <h3>商品规格</h3>
        <dl>
          <template v-for="(value, key) in storefront.detailProduct.specifications" :key="key"
            ><dt>{{ String(key).replaceAll('_', ' ') }}</dt>
            <dd>{{ value }}</dd></template
          >
        </dl>
      </section>
      <section>
        <h3>售后信息</h3>
        <p>
          模拟保修期
          {{ storefront.detailProduct.warranty_months }} 个月。具体规则可向客服询问“保修政策”。
        </p>
      </section>
      <button class="primary-action" type="button" @click="askAssistant">
        <MessageCircle :size="18" />向客服咨询这件商品
      </button>
    </aside>
  </div>
</template>
