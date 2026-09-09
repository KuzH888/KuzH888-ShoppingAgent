<script setup lang="ts">
import { Bot, MessageCircle, Minus, RotateCcw, Send, Sparkles } from '@lucide/vue'
import { nextTick, ref, watch } from 'vue'

import { useChatStore } from '@/stores/chat'
import { useStorefrontStore } from '@/stores/storefront'

const chat = useChatStore()
const storefront = useStorefrontStore()
const draft = ref('')
const messageList = ref<HTMLElement | null>(null)

async function submit() {
  const text = draft.value
  if (!text.trim()) return
  draft.value = ''
  await chat.sendMessage(text, storefront.selectedModel)
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    void submit()
  }
}

watch(
  () => chat.messages.length,
  async () => {
    await nextTick()
    messageList.value?.scrollTo({ top: messageList.value.scrollHeight, behavior: 'smooth' })
  },
)

watch(
  () => chat.suggestedPrompt,
  (prompt) => {
    if (prompt) {
      draft.value = prompt
      chat.suggestedPrompt = ''
    }
  },
)
</script>

<template>
  <aside v-if="chat.isOpen" class="chat-panel" aria-label="KuzMall 智能客服">
    <header class="chat-header">
      <div class="assistant-identity">
        <span><Bot :size="21" /></span>
        <div>
          <strong>KuzBot 智能客服</strong>
          <small><i></i> {{ chat.sending ? '正在思考…' : '在线 · 模拟模式' }}</small>
        </div>
      </div>
      <div class="chat-header-actions">
        <button type="button" title="开始新对话" @click="chat.startNewConversation">
          <RotateCcw :size="17" />
        </button>
        <button type="button" title="收起客服" @click="chat.isOpen = false">
          <Minus :size="18" />
        </button>
      </div>
    </header>

    <div ref="messageList" class="message-list" aria-live="polite">
      <div
        v-for="message in chat.messages"
        :key="message.id"
        class="message-row"
        :class="message.role"
      >
        <span v-if="message.role === 'assistant'" class="message-avatar">
          <Sparkles :size="14" />
        </span>
        <div class="message-bubble">
          {{ message.text }}
          <small v-if="message.mode">{{
            message.mode === 'simulation' ? '本地推荐' : 'LLM 回复'
          }}</small>
        </div>
      </div>
      <div v-if="chat.sending" class="message-row assistant">
        <span class="message-avatar"><Sparkles :size="14" /></span>
        <div class="typing-indicator" aria-label="客服正在输入"><i></i><i></i><i></i></div>
      </div>
    </div>

    <form class="chat-composer" @submit.prevent="submit">
      <textarea
        v-model="draft"
        rows="2"
        maxlength="2000"
        placeholder="例如：100澳元以内适合通勤的降噪耳机"
        aria-label="输入购物需求"
        @keydown="onKeydown"
      ></textarea>
      <button type="submit" :disabled="!draft.trim() || chat.sending" aria-label="发送消息">
        <Send :size="18" />
      </button>
    </form>
    <p class="chat-note">商品信息来自本地目录。按 Shift + Enter 换行。</p>
  </aside>

  <button
    v-else
    class="chat-launcher"
    type="button"
    aria-label="打开智能客服"
    @click="chat.isOpen = true"
  >
    <MessageCircle :size="25" />
    <span>智能选品</span>
  </button>
</template>
