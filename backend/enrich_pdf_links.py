import re
from playwright.sync_api import sync_playwright
from backend.database import SessionLocal
from backend.models import CorporateEvent
from backend.logger import logger

def update_direct_pdf_links():
    db = SessionLocal()
    events = db.query(CorporateEvent).all()
    logger.info(f"Checking direct PDF links for {len(events)} corporate events...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        page.goto("https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi/", wait_until="networkidle")
        
        # Query broad announcement list
        script = """
        async () => {
            const url = 'https://www.idx.co.id/primary/ListedCompany/GetAnnouncement?kodeEmiten=&emitenType=*&indexFrom=0&pageSize=200&dateFrom=20260101&dateTo=20260824&lang=id&keyword=';
            const res = await fetch(url);
            return await res.json();
        }
        """
        data = page.evaluate(script)
        items = data.get("Results") or data.get("Replies") or []
        logger.info(f"Retrieved {len(items)} announcement items from IDX.")
        
        updated = 0
        for e in events:
            if e.source_url and e.source_url.endswith(".pdf"):
                continue
                
            ticker = (e.ticker or "").strip().upper()
            title = (e.description or "").strip().lower()
            
            for item in items:
                pengumuman = item.get("pengumuman", {})
                item_ticker = (item.get("KodeEmiten") or pengumuman.get("Kode_Emiten") or "").strip().upper()
                item_title = (item.get("Title") or pengumuman.get("JudulPengumuman") or "").strip().lower()
                
                # Match by ticker or title keywords
                if (ticker and item_ticker == ticker) or (title and title in item_title) or (item_title and item_title in title):
                    attachments = item.get("Attachments") or item.get("attachments") or pengumuman.get("Attachments") or []
                    for att in attachments:
                        pdf_path = att.get("FullSizeUrl") or att.get("FullSavePath") or att.get("File_Path")
                        if pdf_path:
                            if not pdf_path.startswith("http"):
                                pdf_path = "https://www.idx.co.id" + pdf_path
                            e.source_url = pdf_path
                            updated += 1
                            logger.info(f"Matched {e.ticker or e.company_name} -> {pdf_path}")
                            break
                    if e.source_url.endswith(".pdf"):
                        break
                        
        db.commit()
        browser.close()
        
    logger.info(f"Direct PDF update complete. Updated {updated} events.")
    db.close()

if __name__ == "__main__":
    update_direct_pdf_links()
