import sys
import unittest
from unittest.mock import patch, MagicMock
from datetime import date
sys.path.append('/app')
from backend.scraper import parse_pdf_content
from backend.valuation import calculate_event_valuation
from backend.convergence import link_pre_event_anomalies
from backend.openbb_adapter import fetch_sector_multiples

class E2EDataIntegrityTests(unittest.TestCase):
    def test_ocr_integrity(self):
        # We know from test_ocr_accuracy that the new parsing works without hallucinations
        # We will mock the extracted text directly
        from reportlab.pdfgen import canvas
        import io
        packet = io.BytesIO()
        can = canvas.Canvas(packet)
        text = """
        Nama Perusahaan Tbk: BBCA
        Nama Pemegang Saham: Jahja Setiaatmadja
        Jabatan: Direktur Utama
        Jumlah: 1.000.000
        Harga: 9.000
        Tujuan: Investasi
        Beli
        Sebelum: 10.000.000
        Sesudah: 11.000.000
        Tanggal Transaksi: 05 April 2026
        """
        y = 800
        for line in text.split('\n'):
            can.drawString(10, y, line)
            y -= 20
        can.save()
        packet.seek(0)
        pdf_bytes = packet.read()

        results = parse_pdf_content(pdf_bytes, "https://www.idx.co.id/filings/scanned.pdf", "2026-04-05T00:00:00")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ticker'], "BBCA")
        self.assertEqual(results[0]['shares'], 1000000.0)
        self.assertEqual(results[0]['price'], 9000.0)

    @patch('backend.valuation.yf.Ticker')
    def test_valuation_no_hallucinations(self, mock_ticker):
        # Mocking yf so we don't need network in the test
        mock_info = {
            "trailingPE": 15.5,
            "priceToBook": 2.1,
            "enterpriseToEbitda": 10.0,
            "currentPrice": 1100,
            "previousClose": 1000
        }
        mock_stock = MagicMock()
        mock_stock.info = mock_info

        import pandas as pd
        mock_hist = pd.DataFrame({'Close': [1000.0]})
        mock_stock.history.return_value = mock_hist

        mock_ticker.return_value = mock_stock

        result = calculate_event_valuation("BBCA", date(2026, 4, 5))
        self.assertEqual(float(result["pe_multiple"]), 15.5)
        self.assertEqual(float(result["premium_1d"]), 0.1)

    @patch('backend.openbb_adapter.SessionLocal')
    def test_openbb_adapter(self, mock_session_local):
        import backend.openbb_adapter as adapter

        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Mock the scalar results for pe and pb averages
        mock_db.query.return_value.filter.return_value.scalar.side_effect = [15.0, 2.5]

        res = adapter.fetch_sector_multiples("Financials")
        self.assertEqual(res["sector_pe_avg"], 15.0)
        self.assertEqual(res["sector_pb_avg"], 2.5)

if __name__ == '__main__':
    unittest.main()
