export enum SignalTier {
  HIGH = "HIGH",
  MEDIUM = "MEDIUM",
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
  id?: number;
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
  ownership_after?: number;
  source_url?: string;
  
  // Intelligence Layer
  confidence_score: number; // 0-100
  signal_tier: SignalTier;
  score_reasons: string[];
}

export interface Signal {
  ticker: string;
  title: string;
  body: string;
  severity: SignalTier;
  confidence: number;
  timestamp: string; // ISO DateTime
}

export interface MarketSummary {
  ticker: string;
  last_price: number;
  change_pct: number;
  conviction_score: number;
  signal_tier: SignalTier;
  top_insider_activity: InsiderTransaction[];
}
