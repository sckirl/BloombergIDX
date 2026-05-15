from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Numeric, Boolean, Text, BigInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255))
    sector = Column(String(100))
    subsector = Column(String(100))
    market_cap = Column(BigInteger)
    trailing_pe = Column(Numeric(precision=12, scale=4))
    price_to_book = Column(Numeric(precision=12, scale=4))
    fifty_two_week_high = Column(Numeric(precision=18, scale=4))
    fifty_two_week_low = Column(Numeric(precision=18, scale=4))
    avg_volume = Column(BigInteger)
    listing_date = Column(Date)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    price_ticks = relationship("PriceTick", back_populates="stock")
    broker_transactions = relationship("BrokerTransaction", back_populates="stock")
    insider_filings = relationship("InsiderTransaction", back_populates="stock")
    scores = relationship("SmartMoneyScore", back_populates="stock")
    clusters = relationship("BrokerCluster", back_populates="stock")
    signals = relationship("Signal", back_populates="stock")

class PriceTick(Base):
    __tablename__ = "price_ticks"
    id = Column(BigInteger, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    date = Column(Date, index=True, nullable=False)
    open = Column(Numeric(precision=18, scale=4))
    high = Column(Numeric(precision=18, scale=4))
    low = Column(Numeric(precision=18, scale=4))
    close = Column(Numeric(precision=18, scale=4))
    volume = Column(BigInteger)
    value = Column(BigInteger)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    stock = relationship("Stock", back_populates="price_ticks")

class BrokerTransaction(Base):
    __tablename__ = "broker_transactions"
    id = Column(BigInteger, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    date = Column(Date, index=True, nullable=False)
    broker_code = Column(String(10), index=True, nullable=False)
    broker_name = Column(Text)
    buy_volume = Column(BigInteger)
    sell_volume = Column(BigInteger)
    buy_value = Column(BigInteger)
    sell_value = Column(BigInteger)
    net_value = Column(BigInteger)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    stock = relationship("Stock", back_populates="broker_transactions")

class InsiderTransaction(Base):
    __tablename__ = "insider_transactions"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    ticker = Column(String(10), index=True)
    issuer_name = Column(String(255))
    insider_name = Column(String(255), index=True)
    role = Column(String(100))
    transaction_type = Column(String(20)) # BUY, SELL, GIFT, EXERCISE, INHERITANCE, OTHERS
    shares = Column(Numeric(precision=24, scale=4))
    price = Column(Numeric(precision=18, scale=4))
    value = Column(Numeric(precision=24, scale=4))
    date = Column(Date, index=True) # Actual transaction date
    filing_date = Column(Date, index=True) # Date published on IDX
    ownership_before = Column(Numeric(precision=24, scale=4))
    ownership_after = Column(Numeric(precision=24, scale=4))
    ownership_change_pct = Column(Numeric(precision=12, scale=6))
    direct_ownership = Column(Boolean, default=True)
    purpose = Column(Text)
    source_url = Column(String(511), index=True)
    score = Column(Integer, default=0)
    score_reasons = Column(Text) # JSON string of reasons
    rvol = Column(Numeric(precision=12, scale=4)) # Relative Volume
    is_buyback = Column(Boolean, default=False)
    insider_win_rate = Column(Numeric(precision=12, scale=6)) # Success rate percentage
    price_history = Column(Text) # JSON string of last 5 days
    filing_hash = Column(String(64), index=True)
    date_inferred = Column(Boolean, default=False)
    confidence = Column(Numeric(precision=5, scale=2), default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stock = relationship("Stock", back_populates="insider_filings")
    narrative = relationship("Narrative", back_populates="insider_transaction", uselist=False)

    def __repr__(self):
        return f"<InsiderTransaction(ticker={self.ticker}, name={self.insider_name}, type={self.transaction_type})>"

class Narrative(Base):
    __tablename__ = "narratives"
    id = Column(Integer, primary_key=True, index=True)
    insider_transaction_id = Column(Integer, ForeignKey("insider_transactions.id"), unique=True, index=True)
    state = Column(String(30), default="QUEUED") # NarrativeState
    narrative_text = Column(Text)
    model_version = Column(String(50))
    prompt_version = Column(String(50))
    confidence_score = Column(Numeric(precision=5, scale=2), default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    insider_transaction = relationship("InsiderTransaction", back_populates="narrative")

class SmartMoneyScore(Base):
    __tablename__ = "smart_money_scores"
    id = Column(BigInteger, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    scored_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    score_total = Column(Integer)
    component_broker_flow = Column(Integer)
    component_insider = Column(Integer)
    component_volume = Column(Integer)
    component_repeated_buyer = Column(Integer)
    component_stealth = Column(Integer)
    component_filing = Column(Integer)
    component_momentum = Column(Integer)
    bandar_flag = Column(Boolean, default=False)
    signal_tier = Column(String(20)) # STRONG_BUY, ACCUMULATE, WATCH, NEUTRAL, AVOID

    stock = relationship("Stock", back_populates="scores")

class BrokerCluster(Base):
    __tablename__ = "broker_clusters"
    id = Column(BigInteger, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    broker_codes = Column(Text) # Comma-separated or JSON string
    cluster_type = Column(String(30)) # ACCUMULATION, DISTRIBUTION, CROSS
    window_days = Column(Integer, default=5)
    net_value_idr = Column(BigInteger)
    confidence = Column(Numeric(precision=5, scale=2), default=1.0)
    bandar_proxy = Column(Boolean, default=False)

    stock = relationship("Stock", back_populates="clusters")

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(255), unique=True, nullable=False, index=True)
    name_variants = Column(Text) # JSON array
    entity_type = Column(String(30)) # PERSON, CORP, NOMINEE, PEP
    pep_flag = Column(Boolean, default=False)
    related_entities = Column(Text) # JSON array of IDs or names
    notes = Column(Text)

class Signal(Base):
    __tablename__ = "signals"
    id = Column(BigInteger, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    signal_type = Column(String(40)) # INSIDER_BUY, BANDAR_ACCUM, VOL_ANOMALY, BROKER_CLUSTER
    title = Column(String(255), nullable=False)
    body = Column(Text)
    score_at_signal = Column(Integer)
    severity = Column(String(10)) # HIGH, MED, LOW
    source_ids = Column(Text) # JSON string of causative records

    stock = relationship("Stock", back_populates="signals")

class CorporateEvent(Base):
    __tablename__ = "corporate_events"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), index=True) 
    ticker = Column(String(10), nullable=True, index=True)
    company_name = Column(String(255))
    event_date = Column(Date)

    # Financial Metadata (Sprint-3 Enrichment)
    underwriter = Column(String(255), nullable=True)
    offering_price_range = Column(String(100), nullable=True)
    total_shares = Column(BigInteger, nullable=True)
    acquirer = Column(String(255), nullable=True)
    target = Column(String(255), nullable=True)
    fair_value = Column(Numeric(20, 2), nullable=True)

    # Valuation Multiples (Sprint-3 Logic)
    pe_multiple = Column(Numeric(10, 2), nullable=True)
    pb_multiple = Column(Numeric(10, 2), nullable=True)
    ev_ebitda = Column(Numeric(10, 2), nullable=True)
    premium_1d = Column(Numeric(8, 4), nullable=True)

    # Cross-Module KPIs (Sprint-3)
    pre_event_insider_volume = Column(Numeric(24, 4), nullable=True)
    pre_event_smart_money_score = Column(Integer, nullable=True)
    acquirer_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True)
    target_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True)
    post_event_absorption_ratio = Column(Numeric(12, 4), nullable=True)

    # Temporal State Machine
    status = Column(String(50)) 
    event_version = Column(Integer, default=1)
    source_hash = Column(String(64), unique=True) # PDF/Item hashing
    state_transition_log = Column(Text) # JSON log of history

    description = Column(Text, nullable=True)
    rationale_ai = Column(Text, nullable=True) # AI Enrichment
    source_url = Column(String(500), nullable=True)
    last_seen_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    snapshots = relationship("EventSnapshot", back_populates="event")

class EventSnapshot(Base):
    __tablename__ = "event_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("corporate_events.id"))
    version = Column(Integer)
    status = Column(String(50))
    data_snapshot = Column(Text) # Full JSON dump of state at time
    snapshot_date = Column(DateTime, default=func.now())

    event = relationship("CorporateEvent", back_populates="snapshots")


