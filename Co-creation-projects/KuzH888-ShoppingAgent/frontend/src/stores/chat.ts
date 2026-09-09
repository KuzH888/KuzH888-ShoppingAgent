import { ref } from 'vue'
import { defineStore } from 'pinia'

import { api } from '@/api/client'

export interface ChatMessage {
  id: string
  role: 'assistant' | 'user'
  text: string
  mode?: 'simulation' | 'live'
}

function newSessionId() {
  return crypto.randomUUID()
}

function loadSessionId() {
  const saved = sessionStorage.getItem('kuzmall-session-id')
  if (saved) return saved
  const created = newSessionId()
  sessionStorage.setItem('kuzmall-session-id', created)
  return created
}

const welcomeMessage: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  text: '你好！告诉我你的预算、使用场景和在意的功能，我会从 KuzMall 商品中帮你挑选。\n\nHi! Tell me your budget, use case and must-have features, and I’ll help you choose.',
}

export const useChatStore = defineStore('chat', () => {
  const isOpen = ref(false)
  const sending = ref(false)
  const error = ref('')
  const suggestedPrompt = ref('')
  const sessionId = ref(loadSessionId())
  const messages = ref<ChatMessage[]>([{ ...welcomeMessage }])

  function openWithPrompt(prompt?: string) {
    isOpen.value = true
    suggestedPrompt.value = prompt ?? ''
  }

  async function sendMessage(text: string, modelId: string) {
    const cleaned = text.trim()
    if (!cleaned || sending.value) return

    messages.value.push({ id: crypto.randomUUID(), role: 'user', text: cleaned })
    sending.value = true
    error.value = ''
    try {
      const response = await api.sendMessage(sessionId.value, cleaned, modelId)
      messages.value.push({
        id: crypto.randomUUID(),
        role: 'assistant',
        text: response.message,
        mode: response.mode,
      })
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : '消息发送失败'
      messages.value.push({
        id: crypto.randomUUID(),
        role: 'assistant',
        text: '暂时无法连接智能客服，请确认后端服务正在运行。',
      })
    } finally {
      sending.value = false
    }
  }

  async function startNewConversation() {
    const previous = sessionId.value
    await api.resetSession(previous).catch(() => undefined)
    sessionId.value = newSessionId()
    sessionStorage.setItem('kuzmall-session-id', sessionId.value)
    messages.value = [{ ...welcomeMessage }]
    error.value = ''
  }

  return {
    isOpen,
    sending,
    error,
    suggestedPrompt,
    sessionId,
    messages,
    openWithPrompt,
    sendMessage,
    startNewConversation,
  }
})
