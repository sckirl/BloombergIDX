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
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
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
    shares = Column(Float)
    price = Column(Float)
    value = Column(Float)
    date = Column(Date, index=True) # Actual transaction date
    filing_date = Column(Date, index=True) # Date published on IDX
    ownership_before = Column(Float)
    ownership_after = Column(Float)
    ownership_change_pct = Column(Float)
    direct_ownership = Column(Boolean, default=True)
    purpose = Column(Text)
    source_url = Column(String(511), index=True)
    score = Column(Integer, default=0)
    score_reasons = Column(Text) # JSON string of reasons
    rvol = Column(Float) # Relative Volume
    is_buyback = Column(Boolean, default=False)
    insider_win_rate = Column(Float) # Success rate percentage
    price_history = Column(Text) # JSON string of last 5 days
    date_inferred = Column(Boolean, default=False)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stock = relationship("Stock", back_populates="insider_filings")

    def __repr__(self):
        return f"<InsiderTransaction(ticker={self.ticker}, name={self.insider_name}, type={self.transaction_type})>"

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
    confidence = Column(Float)
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

