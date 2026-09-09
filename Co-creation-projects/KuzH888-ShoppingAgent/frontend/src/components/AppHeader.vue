<script setup lang="ts">
import { Bot, ShoppingBag } from '@lucide/vue'

import { useChatStore } from '@/stores/chat'
import { useStorefrontStore } from '@/stores/storefront'

const storefront = useStorefrontStore()
const chat = useChatStore()
</script>

<template>
  <header class="site-header">
    <a class="brand" href="#catalogue" aria-label="KuzMall 首页">
      <span class="brand-mark"><ShoppingBag :size="21" /></span>
      <span>Kuz<span>Mall</span></span>
    </a>

    <div class="header-actions">
      <label class="model-control">
        <Bot :size="17" />
        <span>客服模型</span>
        <select v-model="storefront.selectedModel" :disabled="storefront.models.length === 0">
          <option v-for="model in storefront.models" :key="model.id" :value="model.id">
            {{ model.label }}
          </option>
        </select>
      </label>
      <button class="header-chat-button" type="button" @click="chat.isOpen = true">咨询客服</button>
    </div>
  </header>
</template>
