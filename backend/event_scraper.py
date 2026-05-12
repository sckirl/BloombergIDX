import json
import re
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from playwright.sync_api import sync_playwright

from .models import CorporateEvent, Stock
from .database import SessionLocal
from .logger import logger

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
            page.goto("https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi/", wait_until="networkidle")
            
            for keyword in keywords:
                logger.info(f"Searching IDX for: {keyword}")
                script = f"""
                async () => {{
                    const url = "https://www.idx.co.id/primary/ListedCompany/GetAnnouncement?kodeEmiten=&emitenType=*&indexFrom=0&pageSize=100&dateFrom={date_from}&dateTo={date_to}&lang=id&keyword=" + encodeURIComponent("{keyword}");
                    const res = await fetch(url);
                    return await res.json();
                }}
                """
                try:
                    data = page.evaluate(script)
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
                                ticker = m_ticker.group(1)
                        
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

                        events.append({
                            "event_type": e_type,
                            "ticker": ticker,
                            "company_name": issuer_name,
                            "event_date": pub_date,
                            "acquirer": acquirer if acquirer else "Undisclosed",
                            "target": target,
                            "status": "PROPOSED", # Default for announcements
                            "description": title,
                            "source_url": "https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi/"
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
            # Deduplication based on company name and event type
            existing = db.query(CorporateEvent).filter(
                CorporateEvent.company_name == e_data["company_name"],
                CorporateEvent.event_type == e_data["event_type"]
            ).first()
            
            if not existing:
                event = CorporateEvent(**e_data)
                db.add(event)
                added_count += 1
                logger.info(f"NEW EVENT: {e_data['event_type']} - {e_data['company_name']}")
            else:
                # Update status and description if they've changed
                has_changed = False
                if existing.status != e_data["status"]:
                    existing.status = e_data["status"]
                    has_changed = True
                
                if existing.description != e_data["description"]:
                    existing.description = e_data["description"]
                    has_changed = True
                
                if has_changed:
                    existing.event_date = e_data["event_date"]
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
