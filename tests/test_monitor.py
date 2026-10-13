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
            self.assertEqual(result['monitoringScope']['flights'], 'disabled_by_user')
            self.assertEqual(result['monitoringScope']['hotelPrices'], 'disabled_by_user')
            self.assertEqual(result['nightlifeStatus'], 'error')
            self.assertNotIn('observedHotelRates', result)

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

    def test_only_current_season_official_body_is_promoted(self):
        body = '<p>Date: December 31, 2026 – January 1, 2027</p><p>Bosingak new year countdown.</p>'
        args = ('Bosingak new year countdown', body, 'https://english.seoul.go.kr/example-announcement/', '2026-10-12T00:00:00Z', '2026-10-13T09:00:00Z')
        briefs = monitor.summarize_official(*args)
        self.assertEqual([b['id'] for b in briefs], ['bosingak'])
        self.assertTrue(briefs[0]['sourceVerified'])
        self.assertEqual(briefs[0]['category'], 'confirmed')
        self.assertEqual(briefs[0]['state'], 'active')
        self.assertIn('普信阁', briefs[0]['name'])
        self.assertEqual(monitor.summarize_official(*[args[0], body, 'https://blog.naver.com/example', *args[3:]]), [])
        self.assertEqual(monitor.summarize_official(*[args[0], body, 'http://english.seoul.go.kr/example-announcement/', *args[3:]]), [])
        self.assertEqual(monitor.summarize_official(*[args[0], body, args[2], '2026-12-01T00:00:00Z', args[4]]), [])

    def test_previous_new_year_and_copyright_do_not_supply_this_season(self):
        body = '<p>Bosingak countdown, December 31, 2025 – January 1, 2026.</p><p>Copyright 2026</p>'
        self.assertEqual(monitor.summarize_official('Welcome 2026', body, 'https://english.seoul.go.kr/archive/', '2026-10-12T00:00:00Z', '2026-10-13T09:00:00Z'), [])
        self.assertEqual(monitor.summarize_official('Bosingak countdown', '<p>December 31, 2026</p>', 'https://english.seoul.go.kr/archive/', '2026-01-01T00:00:00Z', '2026-10-13T09:00:00Z'), [])

    def test_article_excludes_footer_and_widget_dates(self):
        page = '<div id="ct"><p>Bosingak countdown December 31, 2025</p><img src="poster.svg"><p>Old event</p></div><footer>December 31, 2026</footer><div>2027</div>'
        parser = monitor.CityArticle(); parser.feed(page)
        article = ''.join(parser.fragments)
        self.assertNotIn('December 31, 2026', article)
        self.assertEqual(monitor.summarize_official('Bosingak countdown', article, 'https://english.seoul.go.kr/archive/', '2026-10-12T00:00:00Z', '2026-10-13T09:00:00Z'), [])

    def test_current_announcement_does_not_promote_another_events_retrospective(self):
        body = '<p>Seoul Light Gwanghwamun: December 12, 2026.</p><p>Last year: Bosingak countdown December 31, 2025.</p>'
        briefs = monitor.summarize_official('Winter Festa update', body, 'https://english.seoul.go.kr/update/', '2026-10-12T00:00:00Z', '2026-10-13T09:00:00Z')
        self.assertEqual([brief['id'] for brief in briefs], ['gwanghwamun'])

    def test_cancellation_is_not_applied_to_neighboring_events(self):
        body = '<p>December 31, 2026: Seoul Light DDP countdown.</p><p>Bosingak is another new year venue.</p>'
        briefs = monitor.summarize_official('Seoul Light DDP countdown cancelled', body, 'https://english.seoul.go.kr/change/', '2026-10-12T00:00:00Z', '2026-10-13T09:00:00Z')
        self.assertEqual([b['id'] for b in briefs], ['ddp'])
        self.assertEqual(briefs[0]['state'], 'cancelled')

    def test_official_failure_retains_brief_and_original_verification_time(self):
        with tempfile.TemporaryDirectory() as temp:
            output = pathlib.Path(temp) / 'updates.json'
            brief = {'id': 'bosingak', 'sourceVerified': True, 'season': '2026-2027', 'checkedAt': '2026-10-10T00:00:00Z'}
            output.write_text(json.dumps({'items': [], 'eventBriefs': [brief], 'lastOfficialSuccess': '2026-10-10T00:00:00Z'}))
            with patch.object(monitor, 'read', side_effect=OSError('offline')):
                monitor.collect(output)
            result = json.loads(output.read_text())
            self.assertEqual(result['eventBriefs'], [brief])
            self.assertEqual(result['lastOfficialSuccess'], '2026-10-10T00:00:00Z')
            self.assertEqual(result['officialStatus'], 'error')

if __name__ == '__main__':
    unittest.main()
