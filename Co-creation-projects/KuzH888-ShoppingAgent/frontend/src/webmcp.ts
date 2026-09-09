import type { CategoryFilter } from '@/stores/storefront'

interface ToolDefinition {
  name: string
  title: string
  description: string
  inputSchema: Record<string, unknown>
  annotations: { readOnlyHint: boolean; untrustedContentHint: boolean }
  execute: (input: unknown) => unknown
}

interface ModelContext {
  registerTool: (tool: ToolDefinition, options?: { signal?: AbortSignal }) => void | Promise<void>
}

declare global {
  interface Document {
    readonly modelContext?: ModelContext
  }
}

const allowedCategories = ['all', 'digital_accessories', 'home_office', 'travel_lifestyle'] as const

export function registerStorefrontTools(actions: {
  filterCategory: (category: CategoryFilter) => void
  openAssistant: () => void
}) {
  const context = document.modelContext
  if (!context?.registerTool) return () => undefined

  const lifecycle = new AbortController()
  const reportError = (error: unknown) => console.warn('WebMCP tool registration failed', error)

  void Promise.resolve(
    context.registerTool(
      {
        name: 'filter_store_products',
        title: '筛选商城商品',
        description: '按 KuzMall 的一个现有分类筛选当前页面商品。',
        inputSchema: {
          type: 'object',
          properties: { category: { type: 'string', enum: allowedCategories } },
          required: ['category'],
          additionalProperties: false,
        },
        annotations: { readOnlyHint: false, untrustedContentHint: false },
        execute(input) {
          const category = (input as { category?: string })?.category
          if (!allowedCategories.includes(category as (typeof allowedCategories)[number])) {
            throw new Error('Unsupported product category')
          }
          actions.filterCategory(category as CategoryFilter)
          return { category }
        },
      },
      { signal: lifecycle.signal },
    ),
  ).catch(reportError)

  void Promise.resolve(
    context.registerTool(
      {
        name: 'start_shopping_assistant',
        title: '打开智能客服',
        description: '打开当前 KuzMall 页面右下角的智能客服窗口。',
        inputSchema: { type: 'object', properties: {}, additionalProperties: false },
        annotations: { readOnlyHint: false, untrustedContentHint: false },
        execute() {
          actions.openAssistant()
          return { opened: true }
        },
      },
      { signal: lifecycle.signal },
    ),
  ).catch(reportError)

  return () => lifecycle.abort()
}
