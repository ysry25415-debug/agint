/**
 * Type definitions for Product Hunter AI
 */

// Product categories
export enum ProductCategory {
  SMART_GADGETS = 'smart_gadgets',
  MOBILE_ACCESSORIES = 'mobile_accessories',
  PC_GAMING_ACCESSORIES = 'pc_gaming_accessories',
  SMART_HOME = 'smart_home',
  AUDIO_ELECTRONICS = 'audio_electronics',
  PERSONAL_TECHNOLOGY = 'personal_technology',
  INNOVATIVE_PRODUCTS = 'innovative_products',
  PORTABLE_DEVICES = 'portable_devices',
}

// Agent types
export enum AgentType {
  GLOBAL_DISCOVERY = 'global_discovery',
  SOCIAL_TRENDS = 'social_trends',
  EGYPTIAN_MARKET = 'egyptian_market',
  COMPETITOR_ANALYSIS = 'competitor_analysis',
  SUPPLIER_DISCOVERY = 'supplier_discovery',
  PROFIT_CALCULATION = 'profit_calculation',
  PRODUCT_SCORING = 'product_scoring',
  REPORT_GENERATION = 'report_generation',
}

// Execution status
export enum ExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  RETRIED = 'retried',
}

// Source types
export enum SourceType {
  MARKETPLACE = 'marketplace',
  SOCIAL_MEDIA = 'social_media',
  SUPPLIER = 'supplier',
  AGGREGATOR = 'aggregator',
}

// Source status
export enum SourceStatus {
  HEALTHY = 'healthy',
  DEGRADED = 'degraded',
  DOWN = 'down',
  UNKNOWN = 'unknown',
}

// Profit calculation data
export interface ProfitCalculationData {
  supplier_price: number
  supplier_currency: string
  shipping_cost: number
  shipping_currency: string
  customs_duty: number
  customs_fee: number
  local_delivery: number
  marketing_cost: number
  estimated_selling_price: number
  selling_currency: string
}

// Profit report
export interface ProfitReport {
  supplier_purchase_price: number
  supplier_currency: string
  currency_conversion_rate: number
  international_shipping: number
  customs_and_taxes: number
  local_delivery: number
  marketing_costs: number
  total_costs: number
  estimated_selling_price: number
  selling_currency: string
  gross_profit: number
  estimated_net_profit: number
  profit_margin: number
}

// Opportunity score
export interface OpportunityScore {
  id: number
  product_id: number
  total_score: number
  confidence_score: number | null
  demand_signals: number | null
  market_growth: number | null
  competition: number | null
  profit_potential: number | null
  sourcing_feasibility: number | null
  marketing_potential: number | null
  risk_seasonality: number | null
  scored_at: string
  scored_by: string
}

// Score breakdown (for display)
export interface ScoreBreakdown {
  demandSignals: { score: number; max: number; label: string }
  marketGrowth: { score: number; max: number; label: string }
  competition: { score: number; max: number; label: string }
  profitPotential: { score: number; max: number; label: string }
  sourcingFeasibility: { score: number; max: number; label: string }
  marketingPotential: { score: number; max: number; label: string }
  riskSeasonality: { score: number; max: number; label: string }
}

// Telegram notification
export interface TelegramNotification {
  message_id: string
  chat_id: string
  text: string
  photo_url?: string
  reply_markup?: any
  sent_at: string
  status: string
}