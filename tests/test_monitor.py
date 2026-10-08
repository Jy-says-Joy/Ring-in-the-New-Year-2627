import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('monitor', pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'monitor.py')
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)

class MonitorBehavior(unittest.TestCase):
    def test_failure_retains_previous_leads_and_does_not_claim_success(self):
        with tempfile.TemporaryDirectory() as temp:
            output = pathlib.Path(temp) / 'updates.json'
            old = {'lastSuccess': '2026-10-01T01:00:00Z', 'items': [{'title': 'previous lead', 'url': 'https://example.org/', 'discoveredAt': '2026-10-01T01:00:00Z'}]}
            output.write_text(json.dumps(old))
            with patch.object(monitor, 'read', side_effect=OSError('network unavailable')):
                self.assertEqual(monitor.collect(output), 1)
            result = json.loads(output.read_text())
            self.assertEqual(result['status'], 'error')
            self.assertEqual(result['lastSuccess'], old['lastSuccess'])
            self.assertEqual(result['items'], old['items'])
            self.assertEqual(result['priceMonitoring']['flights'], 'not_connected')
            self.assertEqual(result['priceMonitoring']['hotels'], 'error')

    def test_search_results_stay_unverified_and_non_https_links_are_rejected(self):
        rss = b'''<rss><channel><item><title>Old event</title><link>https://example.org/old</link><pubDate>Wed, 31 Dec 2025 12:00:00 GMT</pubDate></item><item><title>Unsafe link</title><link>javascript:alert(1)</link></item></channel></rss>'''
        with tempfile.TemporaryDirectory() as temp:
            output = pathlib.Path(temp) / 'updates.json'
            fixture = pathlib.Path(temp) / 'rss.xml'
            fixture.write_bytes(rss)
            self.assertEqual(monitor.collect(output, str(fixture)), 0)
            result = json.loads(output.read_text())
            self.assertEqual(len(result['items']), 1)
            self.assertEqual(result['items'][0]['status'], 'unverified')
            self.assertTrue(result['items'][0]['publishedAt'].startswith('2025-'))

    def test_hotel_uses_three_night_total_and_rejects_wrong_dates(self):
        body = b'''20261231 20270103 <span class="hotelName">Example Hotel</span><div class="room-name">Standard Twin Room</div><span class="sale">CNY 500</span><span class="price-highlight">CNY 1,800</span>1 room \xc3\x97 3 nights incl. taxes &amp; fees'''
        rates = monitor.hotel_rates(body, '2026-10-08T01:00:00Z')
        self.assertEqual(rates[0]['totalPrice'], 'CNY 1,800')
        self.assertEqual(rates[0]['averageNightly'], 600)
        self.assertTrue(rates[0]['withinBudget'])
        with self.assertRaises(ValueError):
            monitor.hotel_rates(body.replace(b'20270103', b'20260103'), '2026-10-08T01:00:00Z')

if __name__ == '__main__':
    unittest.main()
