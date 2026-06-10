import requests
import json
import time
import io
import re
import base64
import os
import concurrent.futures
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth
import pdfplumber

from .logger import logger
from .database import SessionLocal, engine
from .models import InsiderTransaction, Base, Stock
from .utils import normalize_role, calculate_score, calculate_confidence, get_market_metadata, get_price_on_date, calculate_ownership_change
import threading

# Lock for thread-safe stock creation
stock_creation_lock = threading.Lock()

# Constants
KEYWORDS = ["perubahan kepemilikan", "insider", "saham", "kepemilikan"]
RESERVED_KEYWORDS = ["IDR", "USD", "SAHAM", "TOTAL"]
COMPANY_FORMATS_FILE = os.path.join(os.path.dirname(__file__), "company_formats.json")

def parse_indonesian_number(num_str: str) -> float:
    """
    Intelligently parses numbers from Indonesian IDX reports.
    Handles both 1.000,00 and 1,000.00 formats.
    """
    if not num_str: return 0.0
    num_str = num_str.replace("Rp", "").replace("IDR", "").strip()
    
    # Heuristic to detect format
    last_dot = num_str.rfind(".")
    last_comma = num_str.rfind(",")
    
    if last_comma != -1 and last_dot != -1:
        if last_comma > last_dot:
            # Indonesian format: 1.234.567,89
            num_str = num_str.replace(".", "").replace(",", ".")
        else:
            # US/Standard format: 1,234,567.89
            num_str = num_str.replace(",", "")
    else:
        # Ambiguous (only dot or only comma)
        if last_dot != -1:
            # If dot is followed by exactly 3 digits, it's likely a thousands separator in ID
            parts = num_str.split('.')
            if all(len(p) == 3 for p in parts[1:]):
                num_str = num_str.replace(".", "")
        elif last_comma != -1:
            # If comma is followed by exactly 3 digits, it's likely a thousands separator in US
            if len(num_str) - last_comma == 4:
                num_str = num_str.replace(",", "")
            else:
                num_str = num_str.replace(",", ".")
                
    try:
        # Remove any remaining non-numeric chars except the decimal point
        num_str = re.sub(r"[^\d\.]", "", num_str)
        return float(num_str)
    except:
        return 0.0

# Ensure DB tables are created
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")
except Exception as e:
    logger.error(f"Error creating tables: {e}")

# ... (skip to load_company_formats)
def load_company_formats() -> Dict[str, Any]:
    try:
        if os.path.exists(COMPANY_FORMATS_FILE):
            with open(COMPANY_FORMATS_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading company formats: {e}")
    return {}

def save_company_formats(formats: Dict[str, Any]):
    try:
        with open(COMPANY_FORMATS_FILE, "w") as f:
            json.dump(formats, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving company formats: {e}")

def extract_transaction_date(text: str) -> Optional[datetime.date]:
    """
    Extracts transaction date using common Indonesian and English patterns.
    """
    # Clean text for better matching
    text = text.replace("\n", " ")
    
    date_patterns = [
        # Indonesian: Tanggal Transaksi, Waktu Pelaksanaan, Tanggal Perolehan, etc.
        r"(?:Tanggal Transaksi|Waktu Pelaksanaan|Tanggal Perolehan|Tanggal Penjualan|Tanggal Perubahan|Tanggal Pelaksanaan|Date of Transaction)\s*[:]?\s*(?:[A-Za-z]+,?\s*)?(\d{1,2}[\/\-\.\s](?:Jan(?:uari)?|Feb(?:ruari)?|Mar(?:et)?|Apr(?:il)?|Mei|Jun(?:i)?|Jul(?:i)?|Agu(?:stus)?|Sep(?:tember)?|Okt(?:ober)?|Nov(?:ember)?|Des(?:ember)?)\s*\d{4})",
        # Slash format: 06/04/2026
        r"(?:Tanggal Transaksi|Waktu Pelaksanaan|Tanggal Perolehan|Tanggal Penjualan|Tanggal Perubahan|Tanggal Pelaksanaan|Date of Transaction)\s*[:]?\s*(?:[A-Za-z]+,?\s*)?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        # English: April 10, 2026
        r"(\d{1,2}[\/\-\.\s](?:January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4})",
        r"([A-Z]{3,10}\s+\d{1,2},\s+\d{4})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            date_str = match.group(1).strip()
            try:
                date_str = date_str.replace("Januari", "January").replace("Februari", "February").replace("Maret", "March")
                date_str = date_str.replace("Mei", "May").replace("Juni", "June").replace("Juli", "July")
                date_str = date_str.replace("Agustus", "August").replace("Oktober", "October").replace("Desember", "December")
                
                # Priority: ID/European (DD/MM/YYYY) must come BEFORE US (MM/DD/YYYY)
                # This prevents "05/10/2026" (May 10) from being read as "October 5"
                for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%B %d, %Y", "%d %b %Y"]:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except: continue
            except: pass
    return None

def parse_pdf_content(pdf_bytes: bytes, source_url: str, filing_date_str: str, issuer_name_api: str = "") -> List[Dict[str, Any]]:
    """
    ULTRA-FLEXIBLE PARSER: Specifically tuned for IDX PDF patterns.
    Handles various Indonesian reporting styles and fallbacks.
    """
    transactions = []
    company_formats = load_company_formats()
    
    try:
        full_text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                full_text += page.extract_text(layout=True) or ""
        
        if not full_text.strip(): return []

        # Ticker Extraction
        ticker = "UNKNOWN"
        m_ticker = re.search(r"(?:Nama Perusahaan Tbk|Issuer|Kode Emiten|Kode Saham)\s*[:]?\s*([A-Z]{4})", full_text, re.I)
        if m_ticker: 
            ticker = m_ticker.group(1).upper().strip()
        else:
            m5 = re.search(r"\(([A-Z]{4})\)", full_text)
            if m5: ticker = m5.group(1).upper().strip()

        if ticker == "UNKNOWN" or len(ticker) != 4 or ticker in RESERVED_KEYWORDS:
            return []

        # Transaction Date
        t_date = extract_transaction_date(full_text)
        filing_date = datetime.now().date()
        if filing_date_str:
            try:
                filing_date = datetime.strptime(filing_date_str.split("T")[0], "%Y-%m-%d").date()
            except: pass
        
        final_date = t_date if t_date else filing_date
        date_inferred = (t_date is None)

        # Insider Name & Role
        insider_name = "Unknown"
        m_name = re.search(r"(?:Nama \(sesuai SID\)|Name \(SID\)|Nama)\s*[:]?\s*([^\n]+)", full_text, re.I)
        if m_name: insider_name = m_name.group(1).strip()

        role = ""
        if re.search(r"Anggota Direksi/Dewan Komisaris\s*:\s*Ya", full_text, re.I):
            role = "DIREKTUR"

        # Shares & Price (NLP/Pattern matching)
        shares = 0
        price = 0
        total_value = 0
        ownership_before = 0
        ownership_after = 0
        
        # Pattern 1: Nilai Transaksi Total (Common in KSEI reports)
        m_total = re.search(r"(?:Total Nilai Transaksi|Transaction Value|Nilai Transaksi)\s*[:]?\s*Rp?\s*([\d\.,]+)", full_text, re.I)
        if m_total:
            total_value = parse_indonesian_number(m_total.group(1))

        # Pattern 2: Jumlah Saham Sebelum/Sesudah & Calculate Shares
        before_match = re.search(r"(?:Jumlah Saham Sebelum Transaksi|Number of shares held before|Status Kepemilikan Sebelum)\s*[:]?\s*([\d\.,]+)", full_text, re.I)
        after_match = re.search(r"(?:Jumlah Saham Setelah Transaksi|Number of shares held after|Status Kepemilikan Setelah)\s*[:]?\s*([\d\.,]+)", full_text, re.I)
        
        if before_match:
            ownership_before = parse_indonesian_number(before_match.group(1))
            
        if after_match:
            ownership_after = parse_indonesian_number(after_match.group(1))
            
        if ownership_before > 0 and ownership_after > 0:
            shares = abs(ownership_after - ownership_before)
        
        if shares == 0:
            # Try specific "Jumlah Saham yang dibeli/dijual" patterns
            m_trans_shares = re.search(r"(?:Jumlah Saham yang (?:dibeli|dijual)|Number of shares (?:bought|sold)|Jumlah yang (?:dibeli|dijual))\s*[:]?\s*([\d\.,]+)", full_text, re.I)
            if m_trans_shares:
                shares = parse_indonesian_number(m_trans_shares.group(1))

        if shares == 0:
            # Fallback if specific "Before/After" labels are missing but "Jumlah Saham" exists
            m_shares = re.search(r"(?:Jumlah Saham|Number of Shares|Shares|Jumlah)\s*[:]?\s*([\d\.,]+)", full_text, re.I)
            if m_shares:
                shares = parse_indonesian_number(m_shares.group(1))

        if price == 0 and shares > 0:
            # Pattern 3: Price after shares
            # Look for a number near the shares amount
            shares_str_clean = str(int(shares))
            p_pattern = f"{re.escape(shares_str_clean)}[^\\d]+([\\d\\.,]+)"
            m_price = re.search(p_pattern, full_text)
            if m_price:
                price = parse_indonesian_number(m_price.group(1))

        if price == 0 and shares > 0:
            # Pattern 4: "Harga" followed by price
            m_price2 = re.search(r"(?:Harga|Price|Harga Transaksi|Price of Transaction)\s*[:]?\s*(?:Rp)?\s*([\d\.,]+)", full_text, re.I)
            if m_price2:
                price = parse_indonesian_number(m_price2.group(1))

        if price == 0 and shares > 0 and total_value > 0:
            price = total_value / shares

        if shares == 0 and total_value > 0 and price > 0:
            shares = total_value / price

        # Fallback to Stock API if price is 0
        api_price = get_price_on_date(ticker, final_date)
        
        if price == 0 or price < 1:
            price = api_price
            
        if shares == 0 and total_value > 0 and price > 0:
            shares = total_value / price
        
        if total_value == 0:
            total_value = shares * price

        # If total_value is suspiciously low compared to API, re-calculate
        if api_price > 0 and total_value < (shares * api_price * 0.5):
             price = api_price
             total_value = shares * price

        # Final sanity check: if value is still 0, reject this item
        if total_value == 0 or shares == 0:
            return []

        # Billionaire Sanity Check & Value Cap
        VALUE_CAP = 100_000_000_000_000 # 100 Trillion IDR
        if total_value > VALUE_CAP:
            logger.error(f"CRITICAL: Value for {ticker} (IDR {total_value}) exceeds sanity cap. Rejecting as artifact.")
            return []

        # Record company format
        if shares > 0 and total_value < VALUE_CAP:
             current_fmt = {
                 "last_updated": datetime.now().strftime("%Y-%m-%d"),
                 "shares": shares,
                 "price": price,
                 "date_found": t_date is not None,
                 "total_value_found": total_value > 0
             }
             if ticker not in company_formats:
                company_formats[ticker] = current_fmt
                save_company_formats(company_formats)

        t_type = "SELL" if any(x in full_text.lower() for x in ["jual", "sales", "pengurangan", "pelepasan"]) else "BUY"

        # Ownership Change Percentage Calculation
        change_pct = 0
        if ownership_before > 0:
            change_pct = ((ownership_after - ownership_before) / ownership_before) * 100

        transactions.append({
            "ticker": ticker,
            "issuer_name": issuer_name_api,
            "insider_name": insider_name,
            "role": role, 
            "transaction_type": t_type,
            "shares": float(shares),
            "price": float(price),
            "value": float(total_value),
            "date": final_date,
            "filing_date": filing_date,
            "ownership_before": float(ownership_before),
            "ownership_after": float(ownership_after),
            "ownership_change_pct": float(change_pct),
            "date_inferred": date_inferred,
            "source_url": source_url
        })
    except Exception as e:
        logger.error(f"Parser Error for {source_url}: {e}")
    return transactions

from .cache import invalidate_cache

def process_pdf(pdf_bytes: bytes, url: str, pub_date: str, title: str, issuer_name: str = ""):
    db = SessionLocal()
    try:
        parsed = parse_pdf_content(pdf_bytes, url, pub_date, issuer_name)
        is_buyback = "Pembelian Kembali" in (title or "")
        
        added = 0
        for t_data in parsed:
            t_data["is_buyback"] = is_buyback
            
            # Resolve stock_id with lock to prevent race conditions
            ticker = t_data["ticker"]
            with stock_creation_lock:
                stock = db.query(Stock).filter(Stock.ticker == ticker).first()
                if not stock:
                    # Create stock if it doesn't exist
                    stock = Stock(ticker=ticker, name=issuer_name or f"Company {ticker}")
                    db.add(stock)
                    db.flush() # Get the ID
                elif issuer_name and (not stock.name or stock.name.startswith("Company ")):
                    stock.name = issuer_name
            
            t_data["stock_id"] = stock.id

            m_meta = get_market_metadata(t_data["ticker"])
            t_data["rvol"] = m_meta["rvol"]
            t_data["price_history"] = json.dumps(m_meta["price_history"])
            score, reasons = calculate_score(t_data, db=db)
            t_data["score"] = score
            t_data["score_reasons"] = json.dumps(reasons)
            t_data["confidence"] = calculate_confidence(t_data)
            db.add(InsiderTransaction(**t_data))
            added += 1
        
        db.commit()
        if added > 0:
            logger.info(f"Successfully added {added} rows from {url}.")
            invalidate_cache("insider_*") # Invalidate all insider caches
        return added
    except Exception as e:
        logger.error(f"Error processing {url}: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def run_scraper(full_year=False):
    logger.info(f"Starting Scraper (Full Year: {full_year})")
    db = SessionLocal()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = context.new_page()

        try:

            page.goto("https://www.idx.co.id/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            
            all_items = []
            
            # Using browser context fetch to bypass Cloudflare
            for keyword in KEYWORDS:
                logger.info(f"Searching: {keyword}")
                try:
                    if full_year:
                        # Target entire 2026 year specifically as requested
                        date_from = "20260101"
                        date_to = "20261231"
                        page_size = 5000 # Increased for full year volume coverage
                    else:
                        date_from = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d")
                        date_to = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
                        page_size = 50
                    
                    script = """
                    async ({ page_size, date_from, date_to, keyword }) => {
                        const url = `https://www.idx.co.id/primary/ListedCompany/GetAnnouncement?kodeEmiten=&emitenType=*&indexFrom=0&pageSize=${page_size}&dateFrom=${date_from}&dateTo=${date_to}&lang=id&keyword=` + encodeURIComponent(keyword);
                        const res = await fetch(url);
                        return await res.json();
                    }
                    """
                    data = page.evaluate(script, {
                        "page_size": page_size,
                        "date_from": date_from,
                        "date_to": date_to,
                        "keyword": keyword
                    })
                    items = data.get("Results") or data.get("Replies") or []
                    all_items.extend(items)
                except Exception as e:
                    logger.error(f"Search failed for {keyword}: {e}")

            logger.info(f"Total Disclosures Found: {len(all_items)}")

            # Use a robust requests session for binary fetching (much more stable than browser eval)
            s = requests.Session()
            s.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Referer": "https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi/"
            })

            # Sort by published date descending
            def get_date(x):
                d = x.get("PublishedDate") or x.get("pengumuman", {}).get("TglPengumuman") or ""
                return d

            all_items.sort(key=get_date, reverse=True)
            
            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for item in all_items:
                    pub_date = item.get("PublishedDate") or item.get("pengumuman", {}).get("TglPengumuman")
                    title = item.get("Title") or item.get("pengumuman", {}).get("JudulPengumuman")
                    issuer_name = item.get("IssuerName") or item.get("NamaEmiten") or ""
                    attachments = item.get("Attachments") or item.get("attachments") or []
                    
                    for att in attachments:
                        url = att.get("FullSizeUrl") or att.get("FullSavePath")
                        if not url: continue
                        if not url.startswith("http"): url = "https://www.idx.co.id" + url
                        
                        if db.query(InsiderTransaction).filter(InsiderTransaction.source_url == url).first(): continue
                        
                        logger.info(f"Ingesting: {url}")
                        try:
                            # THE STABILITY FIX: Use requests session instead of page.evaluate
                            resp = s.get(url, timeout=30)
                            if resp.status_code == 200:
                                pdf_bytes = resp.content
                                futures.append(executor.submit(process_pdf, pdf_bytes, url, pub_date, title, issuer_name))
                            else:
                                logger.warning(f"  - Failed to download {url}: Status {resp.status_code}")
                        except Exception as e:
                            logger.error(f"  - Error fetching {url}: {e}")
                        
                        time.sleep(0.2) 
                
                for future in concurrent.futures.as_completed(futures):
                    future.result()
                    
        finally:
            browser.close()
            db.close()
    logger.info("Scraper Finished.")

if __name__ == "__main__":
    import sys
    run_scraper(full_year="--full-year" in sys.argv)
