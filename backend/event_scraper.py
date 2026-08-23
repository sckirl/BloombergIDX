import json
import re
from datetime import datetime, timedelta, date
import hashlib
from sqlalchemy.orm import Session
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth

from .models import CorporateEvent, EventSnapshot, Stock
from .database import SessionLocal
from .logger import logger
from .valuation import calculate_event_valuation
from .convergence import link_pre_event_anomalies
from .openbb_adapter import fetch_sector_multiples

def scrape_e_ipo():
    """
    Scrapes E-IPO data from https://www.e-ipo.co.id/en/ipo/index.
    Uses robust selection and text parsing.
    """
    events = []
    logger.info("Starting E-IPO scraper...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
            page = context.new_page()

            
            # E-IPO website is notoriously slow and often needs multiple attempts or long waits
            page.goto("https://www.e-ipo.co.id/en/ipo/index", wait_until="domcontentloaded", timeout=60000)
            
            # Give it some time to render JS components
            page.wait_for_timeout(7000) 
            
            # Find all cards or rows. E-IPO currently uses a card-based layout.
            cards = page.query_selector_all(".card")
            
            if not cards:
                # Try fallback selectors if the structure changed
                cards = page.query_selector_all("[class*='item']")
            
            logger.info(f"E-IPO: Found {len(cards)} items to analyze.")
            
            for card in cards:
                try:
                    text = card.inner_text()
                    if not text or len(text) < 20: continue
                    
                    # Extract Ticker (usually 4 uppercase letters in a badge or title)
                    ticker_match = re.search(r"\b([A-Z]{4})\b", text)
                    ticker = ticker_match.group(1) if ticker_match else None
                    
                    # Extract Company Name
                    name_elem = card.query_selector("h5") or card.query_selector("h4") or card.query_selector(".title")
                    company_name = name_elem.inner_text().strip() if name_elem else "Unknown Company"
                    
                    if company_name == "Unknown Company" and ticker:
                        company_name = f"PT {ticker} Tbk (Tentative)"

                    # Status mapping
                    status = "PROPOSED"
                    text_lower = text.lower()
                    if "book building" in text_lower: status = "BOOKBUILDING"
                    elif "public offering" in text_lower or "offering" in text_lower: status = "OFFERING"
                    elif "allotment" in text_lower: status = "ALLOTMENT"
                    elif "listing" in text_lower: status = "COMPLETED"
                    elif "postponed" in text_lower or "ditunda" in text_lower: status = "POSTPONED"
                    elif "waiting" in text_lower or "menunggu" in text_lower: status = "WAITING"

                    # Price range
                    price_range = "N/A"
                    price_match = re.search(r"Rp\s*([\d\.,\s-]+)", text)
                    if price_match:
                        price_range = price_match.group(1).strip()
                    
                    # Underwriter
                    underwriter = ""
                    uw_match = re.search(r"(?:Underwriter|Lead)\s*:\s*([^\n]+)", text, re.I)
                    if uw_match:
                        underwriter = uw_match.group(1).strip()
                    
                    # Total shares
                    total_shares = 0
                    shares_match = re.search(r"([\d\.,]+)\s*shares", text, re.I)
                    if shares_match:
                        try:
                            total_shares = int(shares_match.group(1).replace(",", "").replace(".", ""))
                        except: pass

                    # Avoid adding empty or placeholder items
                    if ticker or company_name != "Unknown Company":
                        events.append({
                            "event_type": "E-IPO",
                            "ticker": ticker,
                            "company_name": company_name,
                            "event_date": date.today(),
                            "underwriter": underwriter,
                            "offering_price_range": price_range,
                            "total_shares": total_shares,
                            "status": status,
                            "description": f"Initial Public Offering for {company_name}",
                            "source_url": "https://www.e-ipo.co.id/en/ipo/index"
                        })
                except Exception as e:
                    logger.error(f"Error parsing E-IPO item: {e}")
            
            browser.close()
        except Exception as e:
            logger.error(f"E-IPO scraping failed: {e}")
            
    return events

def scrape_idx_mergers():
    """
    Scrapes IDX announcements for Mergers, Acquisitions, and Takeovers.
    """
    events = []
    logger.info("Starting IDX Merger scraper...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
            page = context.new_page()

            
            keywords = ["Pengambilalihan", "Akuisisi", "Merger"]
            # Look back 60 days for corporate actions
            date_from = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")
            date_to = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
            
            # Navigate to establish session/cookies
            page.goto("https://www.idx.co.id/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            
            for keyword in keywords:
                logger.info(f"Searching IDX for: {keyword}")
                script = """
                async ({date_from, date_to, keyword}) => {
                    const url = `https://www.idx.co.id/primary/ListedCompany/GetAnnouncement?kodeEmiten=&emitenType=*&indexFrom=0&pageSize=100&dateFrom=${date_from}&dateTo=${date_to}&lang=id&keyword=` + encodeURIComponent(keyword);
                    const res = await fetch(url);
                    return await res.json();
                }
                """
                try:
                    data = page.evaluate(script, {"date_from": date_from, "date_to": date_to, "keyword": keyword})
                    items = data.get("Results") or data.get("Replies") or []
                    
                    for item in items:
                        # Extract data with nested fallbacks
                        pengumuman = item.get("pengumuman", {})
                        title = item.get("Title") or pengumuman.get("JudulPengumuman") or ""
                        
                        # The IDX Search API for corporate actions uses 'Kode_Emiten'
                        ticker = item.get("KodeEmiten") or pengumuman.get("Kode_Emiten") or ""
                        issuer_name = item.get("IssuerName") or item.get("NamaEmiten") or pengumuman.get("NamaEmiten") or ""
                        
                        pub_date_str = item.get("PublishedDate") or pengumuman.get("TglPengumuman") or ""
                        
                        # Ticker cleaning
                        if not ticker:
                            m_ticker = re.search(r"\[([A-Z]{4})\]", title)
                            if m_ticker:
                                ticker = m_ticker.group(1).strip()
                        else:
                            ticker = ticker.strip()
                        
                        # If we have a ticker but no issuer name, try to resolve from Stock table
                        if ticker and not issuer_name:
                            db_temp = SessionLocal()
                            try:
                                stock = db_temp.query(Stock).filter(Stock.ticker == ticker).first()
                                if stock:
                                    issuer_name = stock.name
                            finally:
                                db_temp.close()
                        
                        # Final fallback
                        if not issuer_name and ticker:
                            issuer_name = f"PT {ticker} Tbk"
                        
                        pub_date = date.today()
                        if pub_date_str:
                            try:
                                pub_date = datetime.strptime(pub_date_str.split("T")[0], "%Y-%m-%d").date()
                            except: pass
                        
                        # Determine if it's Merger or Acquisition
                        e_type = "ACQUISITION"
                        title_lower = title.lower()
                        if "merger" in title_lower or "penggabungan" in title_lower:
                            e_type = "MERGER"
                        elif "pengambilalihan" in title_lower or "akuisisi" in title_lower or "takeover" in title_lower:
                            e_type = "ACQUISITION"
                        
                        # Institutional Mandate: Only ingest "Actual" events (Success/Penyelesaian/Hasil)
                        # Filter out purely "Proposed" or "Negotiation" items to keep the menu informational
                        status = "PROPOSED"
                        if any(kw in title_lower for kw in ["penyelesaian", "hasil", "completion", "effective", "resmi", "pencatatan"]):
                            status = "COMPLETED"
                        elif any(kw in title_lower for kw in ["jadwal", "rencana", "plan"]):
                            status = "WAITING"
                        
                        # User Mandate: Delete purely speculative/Proposed items if requested, or filter here
                        if status == "PROPOSED":
                            continue

                        # Basic extraction logic for acquirer/target
                        acquirer = ""
                        target = issuer_name
                        
                        # Pattern: "Pengambilalihan [Target] oleh [Acquirer]"
                        m = re.search(r"(?:oleh|by)\s+([A-Za-z0-9\s,\.]+)", title, re.I)
                        if m:
                            acquirer = m.group(1).strip()
                            
                        # If acquirer not found, sometimes it's "[Acquirer] mengumumkan akuisisi [Target]"
                        if not acquirer:
                            m2 = re.search(r"^([A-Za-z0-9\s,\.]+)\s+(?:mengumumkan|melakukan|rencana)", title, re.I)
                            if m2:
                                acquirer = m2.group(1).strip()

                        # Extract Direct PDF Source URL from IDX Attachments
                        attachments = item.get("Attachments") or item.get("attachments") or pengumuman.get("Attachments") or []
                        source_url = "https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi/"
                        for att in attachments:
                            pdf_url = att.get("FullSizeUrl") or att.get("FullSavePath") or att.get("File_Path")
                            if pdf_url:
                                if not pdf_url.startswith("http"):
                                    pdf_url = "https://www.idx.co.id" + pdf_url
                                source_url = pdf_url
                                break

                        events.append({
                            "event_type": e_type,
                            "ticker": ticker,
                            "company_name": issuer_name,
                            "event_date": pub_date,
                            "acquirer": acquirer if acquirer else "Undisclosed",
                            "target": target,
                            "status": "PROPOSED", # Default for announcements
                            "description": title,
                            "source_url": source_url
                        })
                except Exception as e:
                    logger.error(f"Error evaluating IDX script for {keyword}: {e}")
            
            browser.close()
        except Exception as e:
            logger.error(f"IDX Merger scraping failed: {e}")
            
    return events

def run_event_scraper():
    """
    Main entry point for the event scraper.
    """
    db = SessionLocal()
    try:
        logger.info("Starting Corporate Event Scraper Pipeline...")
        
        e_ipo_events = scrape_e_ipo()
        logger.info(f"Scraped {len(e_ipo_events)} E-IPO events.")
        
        merger_events = scrape_idx_mergers()
        logger.info(f"Scraped {len(merger_events)} Merger/Acquisition events.")
        
        all_events = e_ipo_events + merger_events
        
        added_count = 0
        updated_count = 0
        
        for e_data in all_events:
            # Generate a source hash based on key identifying fields
            hash_string = f"{e_data.get('company_name', '')}_{e_data.get('event_type', '')}_{e_data.get('description', '')}_{e_data.get('status', '')}"
            source_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
            e_data["source_hash"] = source_hash

            # Deduplication based on company name and event type
            existing = db.query(CorporateEvent).filter(
                CorporateEvent.company_name == e_data["company_name"],
                CorporateEvent.event_type == e_data["event_type"],
                CorporateEvent.description == e_data["description"]
            ).first()
            
            if not existing:
                # Track B: Enforce Deterministic Valuation from real-world data (yfinance)
                val_data = calculate_event_valuation(e_data["ticker"], e_data["event_date"])
                e_data.update(val_data)

                # Pre-Event Linkage (Convergence Logic)
                conv_data = link_pre_event_anomalies(db, e_data["ticker"], e_data["event_date"])
                e_data.update(conv_data)

                # Fetch OpenBB sector multiples
                stock_record = db.query(Stock).filter(Stock.ticker == e_data["ticker"]).first()
                if stock_record and stock_record.sector:
                    sector_data = fetch_sector_multiples(stock_record.sector)
                    # We don't save sector data straight into corporate events right now but we would use it for benchmarks.
                    # As a proxy we can log it here to ensure integration works.
                    logger.info(f"OpenBB sector multiples for {stock_record.sector}: {sector_data}")

                # Init state transition log
                e_data["state_transition_log"] = json.dumps([{"from": "NONE", "to": e_data["status"], "date": str(e_data["event_date"])}])
                event = CorporateEvent(**e_data)
                db.add(event)
                db.flush()
                # Create initial snapshot
                snapshot = EventSnapshot(
                    event_id=event.id,
                    version=event.event_version,
                    status=event.status,
                    data_snapshot=json.dumps(e_data, default=str)
                )
                db.add(snapshot)
                added_count += 1
                logger.info(f"NEW EVENT: {e_data['event_type']} - {e_data['company_name']}")
            else:
                # Update status and description if they've changed
                has_changed = False
                
                # Check if Sprint-3 Valuation data is missing, if so, force an update
                if existing.pe_multiple is None:
                    val_data = calculate_event_valuation(e_data["ticker"], e_data["event_date"])
                    for k, v in val_data.items():
                        setattr(existing, k, v)
                    has_changed = True

                if existing.pre_event_smart_money_score is None:
                    conv_data = link_pre_event_anomalies(db, e_data["ticker"], e_data["event_date"])
                    for k, v in conv_data.items():
                        setattr(existing, k, v)
                    has_changed = True
                
                if existing.source_hash != source_hash:
                    # Capture state transition if status changed
                    if existing.status != e_data["status"]:
                        log_entry = {"from": existing.status, "to": e_data["status"], "date": str(date.today())}
                        try:
                            transition_log = json.loads(existing.state_transition_log or "[]")
                        except json.JSONDecodeError:
                            transition_log = []
                        transition_log.append(log_entry)
                        existing.state_transition_log = json.dumps(transition_log)
                        existing.status = e_data["status"]
                        has_changed = True

                    if existing.description != e_data["description"]:
                        existing.description = e_data["description"]
                        has_changed = True

                if e_data.get("source_url") and existing.source_url != e_data["source_url"] and ".pdf" in e_data["source_url"].lower():
                    existing.source_url = e_data["source_url"]
                    has_changed = True

                if has_changed:
                    existing.event_date = e_data["event_date"]
                    existing.source_hash = source_hash
                    existing.event_version += 1

                    # Create a new snapshot for the updated version
                    snapshot_data = {k: getattr(existing, k) for k in existing.__dict__.keys() if not k.startswith('_')}
                    snapshot = EventSnapshot(
                        event_id=existing.id,
                        version=existing.event_version,
                        status=existing.status,
                        data_snapshot=json.dumps(snapshot_data, default=str)
                    )
                    db.add(snapshot)

                    updated_count += 1
                    logger.info(f"UPDATED EVENT: {e_data['event_type']} - {e_data['company_name']}")
        
        db.commit()
        logger.info(f"Corporate Event Scraper finished. Added: {added_count}, Updated: {updated_count}")
        
    except Exception as e:
        logger.error(f"Event Scraper Pipeline failed: {e}")
        db.rollback()
    finally:
        db.close()

def seed_initial_events():
    """
    Compatibility wrapper for legacy calls.
    Now triggers the real scraper.
    """
    run_event_scraper()

if __name__ == "__main__":
    run_event_scraper()
