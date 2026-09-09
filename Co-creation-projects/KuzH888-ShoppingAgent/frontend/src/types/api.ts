export type Category = 'digital_accessories' | 'home_office' | 'travel_lifestyle'
export type Language = 'zh' | 'en'

export interface LocalizedText {
  zh: string
  en: string
}

export interface Product {
  id: string
  sku: string
  name: LocalizedText
  description: LocalizedText
  category: Category
  subcategory: string
  price: number
  currency: 'AUD'
  stock: number
  rating: number
  review_count: number
  use_cases: string[]
  features: string[]
  colors: string[]
  warranty_months: number
  specifications: Record<string, unknown>
  image_path: string
}

export interface PublicModel {
  id: string
  label: string
  provider: string
  description_zh: string
  description_en: string
}

export interface ScoredProduct {
  product_id: string
  name: string
  price: number
  currency: string
  score: number
  score_breakdown: Record<string, number>
  matched_requirements: string[]
  tradeoffs: string[]
}

export interface NearMatch {
  product_id: string
  name: string
  price: number
  currency: string
  score: number
  violations: string[]
}

export interface AssistantResult {
  type:
    | 'clarification'
    | 'recommendation'
    | 'no_match'
    | 'product_details'
    | 'comparison'
    | 'policy'
    | 'insufficient_information'
    | 'error'
  language: Language
  message: string
  questions: string[]
  recommendations: ScoredProduct[]
  alternatives: NearMatch[]
  facts: Record<string, unknown>
}

export interface ChatResponse {
  session_id: string
  model_id: string
  mode: 'simulation' | 'live'
  message: string
  result: AssistantResult | null
}

export interface ProductsResponse {
  total: number
  products: Product[]
}

export interface ModelsResponse {
  default_model: string
  models: PublicModel[]
}

export interface ComparisonProduct {
  product_id: string
  name: string
  price: number
  currency: 'AUD'
  stock: number
  rating: number
  features: string[]
  use_cases: string[]
  warranty_months: number
  specifications: Record<string, unknown>
}

export interface StorePolicy {
  id: 'shipping' | 'returns' | 'warranty' | 'privacy'
  title: LocalizedText
  summary: LocalizedText
  details: LocalizedText[]
}
