import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from '@/api/client'
import { useChatStore } from '@/stores/chat'

vi.mock('@/api/client', () => ({
  api: {
    sendMessage: vi.fn(),
    resetSession: vi.fn(),
  },
}))

describe('chat store', () => {
  beforeEach(() => {
    sessionStorage.clear()
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('adds the user and assistant messages', async () => {
    vi.mocked(api.sendMessage).mockResolvedValue({
      session_id: 'test',
      model_id: 'gpt-5.6-luna',
      mode: 'simulation',
      message: '首选：测试商品',
      result: null,
    })
    const store = useChatStore()

    await store.sendMessage('推荐耳机', 'gpt-5.6-luna')

    expect(store.messages.at(-2)?.text).toBe('推荐耳机')
    expect(store.messages.at(-1)?.text).toBe('首选：测试商品')
  })

  it('creates a fresh session for a new conversation', async () => {
    vi.mocked(api.resetSession).mockResolvedValue({ session_id: 'old', reset: true })
    const store = useChatStore()
    const oldId = store.sessionId

    await store.startNewConversation()

    expect(api.resetSession).toHaveBeenCalledWith(oldId)
    expect(store.sessionId).not.toBe(oldId)
    expect(store.messages).toHaveLength(1)
  })
})
