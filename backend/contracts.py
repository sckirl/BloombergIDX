from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class SignalTier(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    GIFT = "GIFT"
    EXERCISE = "EXERCISE"
    INHERITANCE = "INHERITANCE"
    OTHERS = "OTHERS"

class InsiderTransaction(BaseModel):
    id: Optional[int] = None
    ticker: str = Field(..., example="BBCA")
    issuer_name: Optional[str] = None
    insider_name: str
    role: Optional[str] = None
    transaction_type: TransactionType
    shares: float
    price: float
    value: float
    date: date
    filing_date: date
    ownership_after: Optional[float] = None
    source_url: Optional[str] = None
    
    # Intelligence Layer
    confidence_score: int = Field(0, ge=0, le=100)
    signal_tier: SignalTier = SignalTier.LOW
    score_reasons: List[str] = []
    
    class Config:
        orm_mode = True

class Signal(BaseModel):
    ticker: str
    title: str
    body: str
    severity: SignalTier
    confidence: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MarketSummary(BaseModel):
    ticker: str
    last_price: float
    change_pct: float
    conviction_score: int
    signal_tier: SignalTier
    top_insider_activity: List[InsiderTransaction]
