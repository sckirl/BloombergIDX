export enum SignalTier {
  HIGH = "HIGH",
  MED = "MED",
  LOW = "LOW",
}

export enum TransactionType {
  BUY = "BUY",
  SELL = "SELL",
  GIFT = "GIFT",
  EXERCISE = "EXERCISE",
  INHERITANCE = "INHERITANCE",
  OTHERS = "OTHERS",
}

export interface InsiderTransaction {
  id: number;
  stock_id?: number;
  ticker: string;
  issuer_name?: string;
  insider_name: string;
  role?: string;
  transaction_type: TransactionType;
  shares: number;
  price: number;
  value: number;
  date: string; // ISO Date
  filing_date: string; // ISO Date
  ownership_before?: number;
  ownership_after?: number;
  ownership_change_pct?: number;
  direct_ownership?: boolean;
  purpose?: string;
  source_url?: string;
  
  // Intelligence Layer
  score: number;
  score_reasons?: string; // JSON string from backend
  rvol?: number;
  confidence?: number;
  
  // Newly Added from Backend Synchronization
  is_buyback?: boolean;
  insider_win_rate?: number;
  price_history?: string; // JSON string
  date_inferred?: boolean;
}

export interface Signal {
  id: number;
  stock_id?: number;
  ticker?: string; // Often joined
  generated_at: string;
  signal_type: string;
  title: string;
  body: string;
  severity: SignalTier;
  score_at_signal?: number;
}

export interface InsiderCluster {
  ticker: string;
  insider_count: number;
  transaction_count: number;
  last_date: string;
  total_value: number;
  insiders: string[];
  activity: InsiderTransaction[];
}

export interface AbsorptionData {
  ticker: string;
  total_shares_bought: number;
  adv_30d: number;
  absorption_ratio: number;
  current_price: number;
  transaction_count: number;
}
