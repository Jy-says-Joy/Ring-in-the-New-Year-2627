"""Discover Seoul nightlife and validate primary structured event announcements.

Social/search snippets remain leads. Confirmation requires a primary event record
with its own date and Seoul venue; copyright dates and generic club profiles fail.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import html
import json
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

KST = dt.timezone(dt.timedelta(hours=9))
PRIMARY_PATHS = {
    'ra.co': r'^/events/\d+/?$',
    'nol.yanolja.com': r'^/ticket/products/\d+/?$',
    'ticket.yes24.com': r'^/Perf/\d+/?$',
    'faustseoul.com': r'^/', 'www.faustseoul.com': r'^/',
    'cakeshopseoul.com': r'^/', 'www.cakeshopseoul.com': r'^/',
    'www.fourseasons.com': r'^/seoul/',
}
DISCOVERY_QUERIES = [
    ('韩网年末派对与酒吧', '서울 2026 12월 31일 2027 클럽 바 파티'),
    ('公开社交跨年线索', 'site:instagram.com 서울 NYE 2026 2027'),
    ('韩网演出与售票', '서울 2026 12월31일 송년 공연 예매'),
]
PUBLIC_PAGES = [
    ('RA 首尔跨年夜档期', 'https://ra.co/events/kr/seoul?startDate=2026-12-31&endDate=2027-01-01'),
    ('Cakeshop 场地方公告', 'https://cakeshopseoul.com/'),
    ('FAUST 公开社交公告', 'https://www.instagram.com/faustseoul/'),
    ('Cakeshop 公开社交公告', 'https://www.instagram.com/cakeshopseoul/'),
]
VENUES = [
    ('faust', 'FAUST', '梨泰院', ('faust', '파우스트')),
    ('cakeshop', 'Cakeshop', '梨泰院', ('cakeshop', '케이크샵')),
    ('charlesh', 'Charles H.', '光化门', ('charles h', '찰스h', '찰스 h')),
    ('jeanfrigo', 'Jean Frigo', '东大门', ('jean frigo', 'jeanfrigo', '장프리고')),
    ('rollinghall', 'Rolling Hall', '弘大', ('rolling hall', '롤링홀')),
    ('musinsagarage', 'MUSINSA GARAGE', '弘大', ('musinsa garage', '무신사 개러지', '무신사개러지')),
]

class PageData(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.documents = []
        self.script = None
        self.buffer = []
        self.text = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'a':
            url = attributes.get('href', '')
            if urllib.parse.urlsplit(url).scheme == 'https':
                self.links.add(url)
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'script' and attributes.get('type', '').lower() == 'application/ld+json':
            self.script = True
            self.buffer = []
    def handle_endtag(self, tag):
        if tag == 'script' and self.script:
            try:
                self.documents.append(json.loads(''.join(self.buffer)))
            except (ValueError, TypeError):
                pass
            self.script = None
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
    def handle_data(self, value):
        if self.script:
            self.buffer.append(value)
        elif not self.skip and value.strip():
            self.text.append(value.strip())


def primary_url(url):
    parsed = urllib.parse.urlsplit(url)
    return parsed.scheme == 'https' and parsed.hostname in PRIMARY_PATHS and bool(re.match(PRIMARY_PATHS[parsed.hostname], parsed.path))


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def localized_start(value):
    if not isinstance(value, str):
        return None
    try:
        date_only = bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value))
        moment = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=KST)
        moment = moment.astimezone(KST)
        if not (moment.date() == dt.date(2026, 12, 31) or (not date_only and moment.date() == dt.date(2027, 1, 1) and moment.hour < 6)):
            return None
        return moment, date_only
    except (ValueError, TypeError, OverflowError):
        return None


def confirmed_events(body, source_url, checked_at):
    """Only primary Event JSON-LD; an Article/post/search date is insufficient."""
    parser = PageData(); parser.feed(body.decode('utf8', 'replace') if isinstance(body, bytes) else body)
    out = []
    for document in parser.documents:
        for event in objects(document):
            kinds = event.get('@type', [])
            kinds = [kinds] if isinstance(kinds, str) else kinds
            if not isinstance(kinds, list) or not any(k in ('Event', 'MusicEvent', 'DanceEvent', 'SocialEvent') for k in kinds):
                continue
            source = event.get('url') or source_url
            if not isinstance(source, str) or not primary_url(source):
                continue
            # A search page cannot authenticate arbitrary embedded announcements.
            if urllib.parse.urlsplit(source).hostname != urllib.parse.urlsplit(source_url).hostname:
                continue
            if not primary_url(source_url) and not (urllib.parse.urlsplit(source_url).hostname == 'ra.co' and urllib.parse.urlsplit(source_url).path == '/events/kr/seoul'):
                continue
            start = localized_start(event.get('startDate'))
            location = event.get('location')
            if not start or not isinstance(location, dict) or not event.get('name') or not isinstance(location.get('name'), str) or not location['name'].strip():
                continue
            if location.get('@type') == 'VirtualLocation' or str(event.get('eventAttendanceMode', '')).endswith('OnlineEventAttendanceMode'):
                continue
            address = location.get('address', {})
            if isinstance(address, dict):
                # Require the city field, rather than country/nearby metropolitan region.
                locality = str(address.get('addressLocality', ''))
                street = str(address.get('streetAddress', ''))
            elif isinstance(address, str):
                locality, street = address, address
            else:
                continue
            if not re.search(r'\bseoul\b|서울', locality, re.I) or re.search(r'goyang|고양|incheon|인천|suwon|수원', locality, re.I):
                continue
            moment, date_only = start
            name = str(event['name'])
            themed = bool(re.search(r'new.?year|\bnye\b|countdown|카운트다운|새해|송년|연말|신년|뉴이어', name, re.I))
            # Include announced late-night music/DJ events as choices, without
            # inventing a midnight countdown where the listing doesn't promise one.
            if not themed and (date_only or moment.hour < 18 or not any(k in ('MusicEvent', 'DanceEvent') for k in kinds)):
                continue
            venue_name = str(location.get('name', '首尔活动场地'))
            venue_label = venue_name if re.fullmatch(r'[\x20-\x7e]{1,55}', venue_name) else '首尔新场地'
            area, watch_id = '首尔市内', None
            for venue_id, label, district, aliases in VENUES:
                if any(alias in venue_name.lower() for alias in aliases):
                    venue_label, area, watch_id = label, district, venue_id
                    break
            nightclub = watch_id in ('faust', 'cakeshop') or bool(re.search(r'party|dj|club|파티|디제이|클럽', name, re.I)) or any(k in ('DanceEvent', 'SocialEvent') for k in kinds)
            genre = '年末派对' if nightclub else '年末演出'
            artists = event.get('performer', [])
            artists = artists if isinstance(artists, list) else [artists]
            names = [str(a.get('name', '')) for a in artists if isinstance(a, dict)]
            readable = [n for n in names if n and re.fullmatch(r'[\x20-\x7e]{1,70}', n)][:4]
            details = ('公布阵容：' + '、'.join(readable) + '。') if readable else ''
            offers = event.get('offers', [])
            offers = offers if isinstance(offers, list) else [offers]
            offers = [o for o in offers if isinstance(o, dict)]
            prices = []
            for offer in offers[:3]:
                amount, currency = str(offer.get('price', '')), str(offer.get('priceCurrency', ''))
                if re.fullmatch(r'\d+(?:\.\d+)?', amount) and currency in ('KRW', 'USD', 'CNY'):
                    prices.append(currency + ' ' + amount)
            booking = ('公布票面价：' + ' / '.join(dict.fromkeys(prices)) + '；') if prices else ''
            sold_out = bool(offers) and all(str(o.get('availability', '')).endswith('SoldOut') for o in offers)
            booking += '售票页当前标为售罄；留意官方后续放票。' if sold_out else '票种、服务费、入场证件、预约与余票以本次售票页为准。'
            cancelled = str(event.get('eventStatus', '')).endswith(('EventCancelled', 'EventPostponed'))
            stamp = moment.strftime('%Y-%m-%d') + (' · 时段待公布' if date_only else ' ' + moment.strftime('%H:%M')) + ' · KST / UTC+9'
            # Dedicated seller event IDs stay stable when titles or times change.
            identity_key = source if urllib.parse.urlsplit(source).hostname in ('ra.co', 'nol.yanolja.com', 'ticket.yes24.com') else source + '|' + name
            identity = hashlib.sha256(identity_key.encode()).hexdigest()[:16]
            out.append({
                'id': 'primary-' + identity, 'name': venue_label + ' · ' + genre,
                'area': area, 'kind': '派对 / 夜生活' if nightclub else '现场演出',
                'category': 'confirmed', 'season': '2026-2027', 'sourceVerified': True,
                'verification': 'primary_event_record', 'state': 'cancelled' if cancelled else 'active',
                'status': '已公布 · 有取消 / 调整通知' if cancelled else '已公布 · 票务页标为售罄' if sold_out else '主办方 / 票务页已公布',
                'fit': '喜欢这类音乐再选；和同一片区的晚饭组合更从容。',
                'text': details + '这是已公布的年末现场选择。想参加先看音乐风格、入场与散场时间，不把多个主场排在同一个晚上。',
                'history': '本次日期和首尔场地来自活动记录；是否有午夜倒计时、加场或特别节目按主办方公告。',
                'place': venue_name + ', ' + street + ', Seoul', 'time': stamp,
                'booking': booking, 'links': [['本次活动 / 购票页', source]],
                'checkedAt': checked_at, 'startAt': None if date_only else moment.isoformat(),
                'eventDate': moment.date().isoformat(), 'originalName': name,
                'venueWatchId': watch_id,
            })
    return list({card['id']: card for card in out}.values()), parser


def changed_prior_events(page, source_url, previous, checked_at):
    """A unique seller event moved outside the trip must retire its old card."""
    if not primary_url(source_url) or urllib.parse.urlsplit(source_url).hostname not in ('ra.co', 'nol.yanolja.com', 'ticket.yes24.com'):
        return []
    old_cards = [card for card in previous if card.get('verification') == 'primary_event_record' and any(url == source_url for _, url in card.get('links', []))]
    changed = []
    for document in page.documents:
        for event in objects(document):
            kind = event.get('@type', [])
            kinds = [kind] if isinstance(kind, str) else kind
            if not isinstance(kinds, list) or not any(k in ('Event', 'MusicEvent', 'DanceEvent', 'SocialEvent') for k in kinds) or (event.get('url') or source_url) != source_url:
                continue
            raw = event.get('startDate')
            try:
                moment = dt.datetime.fromisoformat(raw.replace('Z', '+00:00'))
            except (ValueError, TypeError, AttributeError):
                continue
            if localized_start(raw):
                continue
            for old in old_cards:
                card = dict(old)
                card.update(state='cancelled', status='活动日期有调整 · 不再列入跨年夜',
                            history='主办方 / 票务页的日期已不在本次跨年夜范围，选择前重新核实。',
                            checkedAt=checked_at)
                changed.append(card)
    return changed


def collect_nightlife(fetch, checked_at, previous=()):
    """Daily Korean/SNS discovery, then bounded primary-page verification."""
    discovery = [('Naver · ' + name, 'https://search.naver.com/search.naver?' + urllib.parse.urlencode({'query': query})) for name, query in DISCOVERY_QUERIES]
    results, leads, candidates = [], {}, set()
    cards = {}
    def get(item):
        name, url = item
        try:
            return name, url, fetch(url), None
        except (OSError, ValueError) as exc:
            return name, url, None, str(exc)[:180]
    with ThreadPoolExecutor(max_workers=6) as pool:
        for name, url, body, error in pool.map(get, discovery + PUBLIC_PAGES):
            if error:
                results.append({'name': name, 'url': url, 'status': 'error', 'error': error})
                continue
            parsed_cards, page = confirmed_events(body, url, checked_at)
            for card in parsed_cards:
                cards[card['id']] = card
            matches = [u for u in page.links if primary_url(u)]
            candidates.update(matches)
            # Instagram account pages without public posts aren't an announcement check.
            restricted = urllib.parse.urlsplit(url).hostname == 'www.instagram.com' and not any('/p/' in u or '/reel/' in u for u in page.links) and not parsed_cards
            results.append({'name': name, 'url': url, 'status': 'error' if restricted else 'ok', 'count': len(parsed_cards), **({'error': '公开页面未提供可读取的活动帖子；不绕过登录验证'} if restricted else {})})
            for target in page.links:
                if primary_url(target) or urllib.parse.urlsplit(target).hostname in ('www.instagram.com', 'blog.naver.com', 'm.blog.naver.com'):
                    leads[target] = {'url': target, 'source': name, 'discoveredAt': checked_at, 'status': 'unverified'}
    # Re-read exact seller/venue pages; search snippets never become confirmed.
    pages = [('主办方 / 票务正文', u) for u in sorted(candidates)[:12]]
    with ThreadPoolExecutor(max_workers=6) as pool:
        for name, url, body, error in pool.map(get, pages):
            if error:
                results.append({'name': name, 'url': url, 'status': 'error', 'error': error}); continue
            parsed, page = confirmed_events(body, url, checked_at)
            if not parsed:
                parsed = changed_prior_events(page, url, previous, checked_at)
            cards.update({entry['id']: entry for entry in parsed})
            results.append({'name': name, 'url': url, 'status': 'ok', 'count': len(parsed)})
    return list(cards.values()), list(leads.values())[:50], results
