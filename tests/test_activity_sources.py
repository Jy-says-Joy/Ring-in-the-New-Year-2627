import importlib.util
import json
import pathlib
import unittest

spec = importlib.util.spec_from_file_location('activity_sources', pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'activity_sources.py')
sources = importlib.util.module_from_spec(spec); spec.loader.exec_module(sources)

class PrimaryAnnouncements(unittest.TestCase):
    def sample(self, **changes):
        event = {'@type': 'MusicEvent', 'name': 'Cakeshop NYE 2026', 'startDate': '2026-12-31T23:00:00+09:00',
                 'url': 'https://ra.co/events/1234567', 'location': {'@type': 'Place', 'name': 'Cakeshop',
                 'address': {'addressLocality': 'Seoul', 'streetAddress': 'Itaewon-ro'}},
                 'offers': {'price': '30000', 'priceCurrency': 'KRW', 'availability': 'https://schema.org/InStock'},
                 'performer': [{'name': 'Example DJ'}]}
        event.update(changes);return event
    def render(self, event, url='https://ra.co/events/1234567'):
        body = '<html><footer>Copyright 2026, Seoul</footer><script type="application/ld+json">'+json.dumps(event)+'</script></html>'
        return sources.confirmed_events(body, url, '2026-10-13T12:00:00Z')[0]
    def test_primary_party_becomes_chinese_card_with_actual_local_time_and_ticket(self):
        cards = self.render(self.sample());self.assertEqual(len(cards), 1)
        card = cards[0];self.assertEqual(card['venueWatchId'], 'cakeshop');self.assertIn('年末派对', card['name'])
        self.assertIn('2026-12-31 23:00', card['time']);self.assertIn('UTC+9', card['time'])
        self.assertIn('30000', card['booking']);self.assertTrue(card['sourceVerified']);self.assertEqual(card['state'], 'active')
    def test_previous_year_does_not_become_current_despite_footer_year(self):
        self.assertEqual(self.render(self.sample(startDate='2025-12-31T23:00:00+09:00')), [])
        self.assertEqual(self.render(self.sample(startDate='2026-01-01T01:00:00+09:00')), [])
    def test_goyang_missing_city_and_virtual_events_are_rejected(self):
        for city in ['Goyang', 'Incheon', '', 'Seoul nearby Goyang']:
            self.assertEqual(self.render(self.sample(location={'name': 'Other club', 'address': {'addressLocality': city}})), [])
        self.assertEqual(self.render(self.sample(eventAttendanceMode='https://schema.org/OnlineEventAttendanceMode')), [])
        self.assertEqual(self.render(self.sample(location={'name':'', 'address':{'addressLocality':'Seoul'}})), [])
    def test_search_snippet_post_dates_and_malicious_authority_do_not_confirm(self):
        self.assertEqual(self.render(self.sample(), 'https://search.naver.com/search.naver?query=NYE'), [])
        self.assertEqual(self.render(self.sample(url='https://ra.co.evil.example/events/123')), [])
        self.assertEqual(self.render({'@type':'Article','name':'NYE','datePublished':'2026-12-31'}), [])
    def test_utc_date_is_converted_to_seoul_before_season_check(self):
        cards=self.render(self.sample(startDate='2026-12-31T16:00:00Z'))
        self.assertIn('2027-01-01 01:00', cards[0]['time'])
        self.assertEqual(self.render(self.sample(startDate='2027-01-01T10:00:00Z')), [])
    def test_date_only_never_invents_midnight_and_cancellation_is_preserved(self):
        cards=self.render(self.sample(startDate='2026-12-31', eventStatus='https://schema.org/EventCancelled'))
        self.assertIn('时段待公布',cards[0]['time']);self.assertNotIn('00:00',cards[0]['time'])
        self.assertEqual(cards[0]['state'],'cancelled')
    def test_regular_daytime_concert_needs_year_end_theme_but_late_live_is_a_choice(self):
        self.assertEqual(self.render(self.sample(name='Regular concert',startDate='2026-12-31T13:00:00+09:00')), [])
        self.assertEqual(len(self.render(self.sample(name='Late live session',startDate='2026-12-31T22:00:00+09:00'))),1)
    def test_daily_discovery_reads_primary_page_instead_of_promoting_search_text(self):
        event=self.sample();page='<script type="application/ld+json">'+json.dumps(event)+'</script>'
        def fetch(url):
            if url=='https://ra.co/events/1234567':return page.encode()
            if 'search.naver.com' in url:return b'<p>NYE 2026 Seoul: unverified snippet</p><a href="https://ra.co/events/1234567">tickets</a>'
            raise OSError('unavailable')
        cards,leads,results=sources.collect_nightlife(fetch,'2026-10-13T12:00:00Z')
        self.assertEqual(len(cards),1);self.assertTrue(all(l['status']=='unverified' for l in leads))
        self.assertTrue(any(s['status']=='error' for s in results))
    def test_all_source_failures_are_reported_instead_of_zero_new_announcements(self):
        def fail(url):raise OSError('blocked')
        cards,leads,results=sources.collect_nightlife(fail,'2026-10-13T12:00:00Z')
        self.assertEqual(cards,[]);self.assertTrue(results);self.assertTrue(all(s['status']=='error' for s in results))

    def test_seller_rescheduling_retires_previously_confirmed_card(self):
        old=self.render(self.sample())
        changed='<script type="application/ld+json">'+json.dumps(self.sample(startDate='2027-01-02T23:00:00+09:00'))+'</script>'
        def fetch(url):
            if url=='https://ra.co/events/1234567':return changed.encode()
            if 'search.naver.com' in url:return b'<a href="https://ra.co/events/1234567">event</a>'
            raise OSError('blocked')
        cards,_,_=sources.collect_nightlife(fetch,'2026-10-14T12:00:00Z',old)
        self.assertEqual(len(cards),1);self.assertEqual(cards[0]['id'],old[0]['id'])
        self.assertEqual(cards[0]['state'],'cancelled')

    def test_seller_title_edit_does_not_create_duplicate_event_id(self):
        before=self.render(self.sample())[0]
        after=self.render(self.sample(name='Cakeshop New Year Eve updated lineup'))[0]
        self.assertEqual(before['id'],after['id'])

if __name__=='__main__':unittest.main()
