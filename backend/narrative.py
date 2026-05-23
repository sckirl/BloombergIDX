import os
from enum import Enum
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
from .cache import redis_client, CustomEncoder
from .models import InsiderTransaction, Narrative
from .database import SessionLocal
from .logger import logger
from openai import AsyncOpenAI

class NarrativeState(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED_RETRYABLE = "FAILED_RETRYABLE"
    FAILED_FINAL = "FAILED_FINAL"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    STALE = "STALE"
    DEGRADED = "DEGRADED"

async def process_narrative_async(txn_id: int, sso: Dict[str, Any], confidence: float = 1.0):
    """
    Asynchronous narrative generator using NVIDIA Nemotron.
    Transitions through NarrativeState based on result.
    """
    logger.info(f"AI Worker: Starting narrative generation for ID {txn_id}...")
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        logger.error("NVIDIA_API_KEY not found in environment.")
        NarrativeStore.set_state(txn_id, NarrativeState.DEGRADED, "AI configuration missing.", confidence=confidence)
        return

    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )

    context = build_compact_context(sso)
    
    # SYSTEM PROMPT: Institutional, dense, Bloomberg-style
    system_prompt = (
        "You are a Bloomberg-grade financial analyst. "
        "Summarize the following Indonesian insider transaction. "
        "Focus on: conviction, historical context, and potential signal. "
        "Tone: Institutional, concise, professional. "
        "Max 300 characters. No filler."
    )

    # Fetch model from environment or fallback to institutional default
    # Resilient check for both MODEL and MODE keys
    model_name = os.getenv("NVIDIA_MODEL") or os.getenv("NVIDIA_MODE") or "nvidia/nemotron-mini-4b-instruct"

    try:
        # 1. Immediate state transition
        NarrativeStore.set_state(txn_id, NarrativeState.PROCESSING, confidence=confidence)
        
        # 2. Call NVIDIA
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
        )
        
        narrative_text = response.choices[0].message.content.strip()
        
        # 3. Final Success state
        NarrativeStore.set_state(txn_id, NarrativeState.SUCCESS, narrative_text, confidence=confidence)
        logger.info(f"Narrative SUCCESS for ID {txn_id}")
        
    except Exception as e:
        error_msg = str(e).lower()
        logger.error(f"NVIDIA API Error for ID {txn_id}: {e}")
        
        # Resilience: Handle timeouts and rate limits
        if "rate limit" in error_msg or "429" in error_msg:
            NarrativeStore.set_state(txn_id, NarrativeState.RATE_LIMITED, confidence=confidence)
        elif "timeout" in error_msg:
            NarrativeStore.set_state(txn_id, NarrativeState.TIMEOUT, confidence=confidence)
        else:
            NarrativeStore.set_state(txn_id, NarrativeState.FAILED_RETRYABLE, confidence=confidence)

class NarrativeStore:
    """Redis-backed state management for AI Narratives with DB persistence."""
    PREFIX = "narrative:state:"
    
    @classmethod
    def _get_key(cls, transaction_id: int) -> str:
        return f"{cls.PREFIX}{transaction_id}"

    @classmethod
    def set_state(cls, transaction_id: int, state: NarrativeState, text: Optional[str] = None, confidence: Optional[float] = None, ttl: int = 86400):
        # 1. Update Redis (Fast path for UI polling)
        if redis_client:
            key = cls._get_key(transaction_id)
            payload = {"state": state.value, "text": text, "confidence": confidence}
            try:
                redis_client.setex(key, ttl, json.dumps(payload, cls=CustomEncoder))
                logger.info(f"NarrativeStore (Redis): ID {transaction_id} -> {state.value}")
            except Exception as e:
                logger.error(f"NarrativeStore.set_state (Redis) failed: {e}")

        # 2. Update Database (Persistence path)
        db = SessionLocal()
        try:
            narrative = db.query(Narrative).filter(Narrative.insider_transaction_id == transaction_id).first()
            if not narrative:
                narrative = Narrative(insider_transaction_id=transaction_id)
                db.add(narrative)
            
            narrative.state = state.value
            if text:
                narrative.narrative_text = text
            if confidence is not None:
                narrative.confidence_score = confidence
            narrative.updated_at = datetime.now()
            db.commit()
            logger.info(f"NarrativeStore (DB): ID {transaction_id} -> {state.value} PERSISTED")
        except Exception as e:
            logger.error(f"NarrativeStore.set_state (DB) failed for ID {transaction_id}: {e}")
            db.rollback()
        finally:
            db.close()

    @classmethod
    def get_state(cls, transaction_id: int) -> Optional[Dict[str, Any]]:
        # 1. Try Redis first
        if redis_client:
            try:
                data = redis_client.get(cls._get_key(transaction_id))
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"NarrativeStore.get_state (Redis) failed: {e}")

        # 2. Fallback to Database
        db = SessionLocal()
        try:
            narrative = db.query(Narrative).filter(Narrative.insider_transaction_id == transaction_id).first()
            if narrative:
                return {
                    "state": narrative.state,
                    "text": narrative.narrative_text,
                    "confidence": float(narrative.confidence_score) if narrative.confidence_score else None
                }
        except Exception as e:
            logger.error(f"NarrativeStore.get_state (DB) failed: {e}")
        finally:
            db.close()
        
        return None

def normalize_to_sso(txn: InsiderTransaction, clusters: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Structured Signal Object (SSO) normalization.
    Flattens transaction data into a high-density intelligence object.
    """
    # Defensive defaults for institutional density
    rvol = float(txn.rvol) if txn.rvol is not None else 1.0
    win_rate = float(txn.insider_win_rate) if txn.insider_win_rate is not None else 0.0

    return {
        "id": txn.id,
        "tkr": txn.ticker,
        "ins": txn.insider_name,
        "role": txn.role,
        "type": txn.transaction_type,
        "val": float(txn.value) if txn.value else 0,
        "shr": float(txn.shares) if txn.shares else 0,
        "prc": float(txn.price) if txn.price else 0,
        "dte": txn.date.isoformat() if txn.date else None,
        "fil": txn.filing_date.isoformat() if txn.filing_date else None,
        "obf": float(txn.ownership_before) if txn.ownership_before else 0,
        "oaf": float(txn.ownership_after) if txn.ownership_after else 0,
        "pct": float(txn.ownership_change_pct) if txn.ownership_change_pct else 0,
        "purp": txn.purpose,
        "scr": txn.score,
        "rvol": rvol,
        "win": win_rate,
        "cls": clusters or []
    }

def build_compact_context(sso: Dict[str, Any]) -> str:
    """
    Compact Context Builder (CCB).
    Generates a dense string representation for LLM ingestion.
    HARD CAP: 1,500 characters.
    """
    # Keys optimized for token efficiency while remaining human/LLM readable
    lines = [
        f"T:{sso['tkr']}|I:{sso['ins']}|R:{sso['role']}",
        f"A:{sso['type']}|V:{sso['val']:,.0f}|S:{sso['shr']:,.0f}|P:{sso['prc']:,.2f}",
        f"D:{sso['dte']}|F:{sso['fil']}|C:{sso['pct']}%|P:{sso['purp']}",
        f"Q:SCR={sso['scr']},RV={sso['rvol']},WR={sso['win']}%"
    ]
    if sso['cls']:
        lines.append(f"CL:{json.dumps(sso['cls'])}")
    
    context = "\n".join(lines)
    return context[:1500]

def token_guard_hash(filing_hash: str, prompt_version: str) -> str:
    """
    TOKEN-GUARD: Generates a unique hash for deduplication.
    Prevents redundant LLM calls for the same filing and logic version.
    """
    return hashlib.sha256(f"{filing_hash}:{prompt_version}".encode()).hexdigest()
