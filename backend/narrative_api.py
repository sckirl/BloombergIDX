from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .database import get_db
from .models import InsiderTransaction
from .narrative import NarrativeStore, NarrativeState, normalize_to_sso, process_narrative_async
import asyncio

router = APIRouter()

@router.get("/insider/narrative/{txn_id}")
async def get_narrative(txn_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Check if we have a stored state
    stored = NarrativeStore.get_state(txn_id)
    if stored:
        # If it was a retryable failure, maybe re-queue?
        # For now, if it's FAILED_RETRYABLE, RATE_LIMITED or TIMEOUT, we allow one retry if requested
        # But to keep it simple and follow the mandate, we just return the stored state.
        return stored
    
    # 2. Fetch transaction
    txn = db.query(InsiderTransaction).filter(InsiderTransaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # 3. Build SSO context
    sso = normalize_to_sso(txn)
    
    # 4. Initialize as QUEUED and trigger background worker
    NarrativeStore.set_state(txn_id, NarrativeState.QUEUED)
    background_tasks.add_task(process_narrative_async, txn_id, sso)
    
    # Return initial state
    return {"state": NarrativeState.QUEUED, "text": "Narrative generation queued."}

@router.get("/insider/sso/{txn_id}")
def get_sso(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(InsiderTransaction).filter(InsiderTransaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return normalize_to_sso(txn)
