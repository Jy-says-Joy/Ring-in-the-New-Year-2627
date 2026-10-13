"""Collect public search leads. Never turn search snippets into confirmed events or fares."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import html
from html.parser import HTMLParser
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = [
    ('普信阁与首尔城市跨年', '서울 보신각 제야의 종 "2026" "2027"'),
    ('光化门灯光与市集', '서울라이트 광화문 마켓 "2026" "12월"'),
    ('DDP 跨年与 SEOULCon', 'DDP 서울콘 카운트다운 "2026" "2027"'),
    ('清溪川冬季灯节', '서울빛초롱축제 "2026" "12월"'),
    ('高阳 CDF 周边备选', 'COUNTDOWN FANTASY "2026-2027"'),
]
OFFICIAL = [('MINT PAPER 主办方首页变化（不等于当届公告）', 'https://www.mintpaper.co.kr/'),
            ('首尔市英文首页变化（不等于跨年公告）', 'https://english.seoul.go.kr/'),
            ('NOL 当届票务页变化（可能含倒计时等动态变化）', 'https://nol.yanolja.com/ticket/products/26014480')]
HOTEL_URL = 'https://www.trip.com/hotels/list?city=274&checkin=2026-12-31&checkout=2027-01-03&adult=2&crn=1&curr=CNY'
OFFICIAL_FEED = 'https://english.seoul.go.kr/feed/'
OFFICIAL_SEARCH = 'https://search.naver.com/search.naver?' + urllib.parse.urlencode({
    'query': 'site:english.seoul.go.kr "2026" "December" "2027" festival countdown'})
ALIASES = {
    'bosingak': ('bosingak', 'bell-ringing', 'bell ringing'),
    'gwanghwamun': ('seoul light gwanghwamun', 'gwanghwamun media'),
    'ddp': ('seoul light ddp', 'ddp countdown', 'countdown at ddp'),
    'seoulcon': ('seoulcon', 'seoul con', 'world k-pop festival'),
    'lantern': ('seoul lantern festival',),
    'market': ('gwanghwamun market', 'gwanghwamun christmas market'),
}
SEASON_DATE = re.compile(
    r'\b(?:dec(?:ember)?\.?\s+\d{1,2}(?:\s*[–-]\s*\d{1,2})?[,\s]*(?:\([^)]*\)[,\s]*)?2026'
    r'|2026[,\s]*(?:dec(?:ember)?\.?\s+\d{1,2})'
    r'|2026\s*[./-]\s*12\s*[./-]\s*\d{1,2}'
    r'|2026년\s*12월\s*\d{1,2})\b', re.I)

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
    def handle_data(self, value):
        if not self.skip and value.strip():
            self.parts.append(value.strip())

def plain(body):
    parser = Text()
    parser.feed(body)
    return '\n'.join(parser.parts)

def summarize_official(title, body, url, published_at, checked_at):
    """Chinese cards require an official article body with this December's full date.

    Search headlines, copyright years and January-2026 reports never establish
    the 2026→2027 season. Existing curated descriptions explain the experience;
    new schedules and purchase rules always remain attached to the announcement.
    """
    origin = urllib.parse.urlsplit(url)
    if origin.scheme != 'https' or origin.hostname != 'english.seoul.go.kr':
        return []
    if not published_at or not ('2026-07-01' <= published_at[:10] <= checked_at[:10]):
        return []
    text = plain(body)
    if not SEASON_DATE.search(text):
        return []
    combined = (title + '\n' + text).lower()
    if not any(word in combined for word in ('new year', 'countdown', 'winter festa', 'lantern festival', 'gwanghwamun market', 'seoul light')):
        return []
    catalog = {event['id']: event for event in json.loads((ROOT / 'public' / 'guide.json').read_text())['events']}
    cards = []
    for event_id, aliases in ALIASES.items():
        if event_id not in catalog or not any(alias in combined for alias in aliases):
            continue
        old = catalog[event_id]
        cancelled = bool(re.search(r'cancel(?:led|ed|lation)|postpon(?:ed|ement)', title, re.I))
        if cancelled and not any(alias in title.lower() for alias in aliases):
            # A cancellation headline about one event must not cancel every
            # neighboring venue mentioned in the article.
            continue
        card = {key: old[key] for key in ['id', 'name', 'area', 'kind', 'fit', 'text', 'place']}
        card.update({
            'category': 'confirmed', 'season': '2026-2027', 'sourceVerified': True,
            'state': 'cancelled' if cancelled else 'active',
            'status': '官方有取消 / 调整通知' if cancelled else '今年官方公告已公布',
            'history': '今年官方公告已列出该项目。往年演出、烟花、规模和票价不自动适用于今年。',
            'time': '2026 年末 · 韩国 KST / UTC+9；完整日期、开放与演出时段见官方公告',
            'booking': '购票、预约、免费入场及交通管制按本次官方公告；不要沿用往届规则。',
            'links': [['今年官方公告', url]], 'checkedAt': checked_at,
            'publishedAt': published_at,
        })
        cards.append(card)
    return cards

class ArticleLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
    def handle_starttag(self, tag, attrs):
        url = dict(attrs).get('href', '')
        parsed = urllib.parse.urlsplit(url)
        if tag == 'a' and parsed.scheme == 'https' and parsed.hostname == 'english.seoul.go.kr' and parsed.path not in ('/', '/feed/') and not parsed.query:
            self.links.add(url)

class CityArticle(HTMLParser):
    """Read only the official article, excluding dated footer/chat widgets."""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.fragments = []
    def handle_starttag(self, tag, attrs):
        if not self.depth and dict(attrs).get('id') == 'ct':
            self.depth = 1
        elif self.depth and tag not in self.VOID:
            self.depth += 1
        if self.depth:
            self.fragments.append(self.get_starttag_text())
    def handle_endtag(self, tag):
        if self.depth:
            self.fragments.append(f'</{tag}>')
            if tag not in self.VOID:
                self.depth -= 1
    def handle_data(self, value):
        if self.depth:
            self.fragments.append(html.escape(value))

def official_candidates(fetch= None):
    """Native city feed plus Naver discovery; read the actual city article."""
    fetch = fetch or read
    articles = []
    errors = []
    try:
        root = ET.fromstring(fetch(OFFICIAL_FEED))
        if root.tag != 'rss':
            raise ValueError('City feed is not RSS')
        for row in root.findall('./channel/item')[:20]:
            title = row.findtext('title', '')
            body = row.findtext('{http://purl.org/rss/1.0/modules/content/}encoded', '')
            articles.append((title, body, row.findtext('link', ''), published(row.findtext('pubDate', ''))))
    except (urllib.error.URLError, OSError, ET.ParseError, ValueError) as exc:
        errors.append(str(exc)[:180])
    try:
        parser = ArticleLinks(); parser.feed(fetch(OFFICIAL_SEARCH).decode('utf8', 'replace'))
        for url in sorted(parser.links)[:8]:
            page = fetch(url).decode('utf8', 'replace')
            title = re.search(r'<title[^>]*>(.*?)</title>', page, re.S | re.I)
            article = CityArticle(); article.feed(page)
            body_text = ''.join(article.fragments)
            date = re.search(r'Registration date\s*(\d{2})/(\d{2})/(2026)', plain(page))
            if date:
                stamp = f'{date[3]}-{date[1]}-{date[2]}T00:00:00+09:00'
                articles.append((plain(title[1]) if title else '', body_text, url, stamp))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        errors.append(str(exc)[:180])
    if not articles and len(errors) == 2:
        raise ValueError('; '.join(errors))
    return articles, errors

def hotel_rates(body, checked_at, url=HOTEL_URL):
    """Only visible twin-room, three-night totals; never use headline nightly teaser prices."""
    page = body.decode('utf-8', 'replace')
    if not all(value in page for value in ['20261231', '20270103', '1 room', '3 nights']):
        raise ValueError('Hotel response did not confirm selected full dates and occupancy')
    rates = []
    for fragment in re.split(r'<span class="hotelName">', page)[1:]:
        name = html.unescape(fragment.split('<', 1)[0])
        room = re.search(r'<div class="room-name">([^<]+)</div>', fragment)
        price = re.search(r'<span class="price-highlight">([^<]+)</span>\s*1 room × 3 nights incl\. taxes &amp; fees', fragment)
        if not room or not price or 'twin' not in room.group(1).lower():
            continue
        amount = html.unescape(price.group(1)).strip()
        if not re.fullmatch(r'(CNY\s*|US\$)[\d,]+(?:\.\d+)?', amount):
            continue
        currency = 'CNY' if amount.startswith('CNY') else 'USD'
        total = float(re.sub(r'[^\d.]', '', amount))
        text = Text(); text.feed(fragment.split('Check Availability', 1)[0])
        raw = '\n'.join(text.parts)
        cancel = '列表显示 Free Cancellation；截止日期和完整条款待订单页核实' if 'Free Cancellation' in raw else '列表显示 4-hour Cancellation Window；不能视为入住前可免费取消' if '4-hour Cancellation Window' in raw else '取消与付款条款待订单页核实'
        rates.append({'name': name, 'room': html.unescape(room.group(1)), 'totalPrice': amount,
                      'averageNightly': round(total / 3, 2), 'currency': currency,
                      'conditions': cancel, 'url': url, 'checkedAt': checked_at,
                      'dates': ['2026-12-31', '2027-01-03'], 'adults': 2, 'rooms': 1,
                      'status': 'listing_observation', 'withinBudget': total <= 6000 if currency == 'CNY' else None})
    return rates

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')

def read(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'SeoulNewYearGuide/1.0 (+public news monitoring)', 'Accept': 'application/rss+xml,text/html;q=0.8'})
    with urllib.request.urlopen(req, timeout=25) as response:
        final = urllib.parse.urlsplit(response.url)
        if urllib.parse.urlsplit(url).hostname == 'english.seoul.go.kr' and (final.scheme != 'https' or final.hostname != 'english.seoul.go.kr'):
            raise ValueError('Official source redirected outside the verified city origin')
        body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise ValueError('response exceeded size limit')
        return body

def published(raw):
    try:
        stamp = parsedate_to_datetime(raw)
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=dt.timezone.utc)
        return stamp.isoformat()
    except (ValueError, TypeError, OverflowError):
        return None

def collect(output, fixture=None):
    prior = json.loads(output.read_text()) if output.exists() else {'items': [], 'lastSuccess': None, 'officialPages': {}}
    attempted = now()
    # Keep old leads on a source failure; don't erase useful previous observations.
    items = {entry['url']: entry for entry in prior.get('items', [])}
    source_results = []
    official_pages = dict(prior.get('officialPages', {}))
    observed_rates = prior.get('observedHotelRates', [])
    hotel_status = 'not_started'
    briefs = {entry['id']: entry for entry in prior.get('eventBriefs', [])}
    official_status = 'not_started'
    last_official_success = prior.get('lastOfficialSuccess')
    successes = 0
    for name, query in SOURCES:
        url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': query, 'hl': 'ko', 'gl': 'KR', 'ceid': 'KR:ko'})
        try:
            body = pathlib.Path(fixture).read_bytes() if fixture else read(url)
            tree = ET.fromstring(body)
            if tree.tag != 'rss':
                raise ValueError('response is not an RSS feed')
            rows = tree.findall('./channel/item')
            for row in rows[:15]:
                target = row.findtext('link', '')
                if urllib.parse.urlsplit(target).scheme != 'https':
                    continue
                entry = {'title': row.findtext('title', '无标题'), 'url': target,
                         'source': row.findtext('source', name), 'publishedAt': published(row.findtext('pubDate', '')),
                         'discoveredAt': items.get(target, {}).get('discoveredAt', attempted), 'status': 'unverified'}
                items[target] = entry
            successes += 1
            source_results.append({'name': name, 'url': url, 'status': 'ok', 'count': len(rows)})
        except (urllib.error.URLError, OSError, ET.ParseError, ValueError) as exc:
            source_results.append({'name': name, 'url': url, 'status': 'error', 'error': str(exc)[:220]})
    if not fixture:
        for name, url in OFFICIAL:
            try:
                digest = hashlib.sha256(read(url)).hexdigest()
                old = official_pages.get(url, {})
                changed = bool(old.get('sha256') and old['sha256'] != digest)
                official_pages[url] = {'sha256': digest, 'checkedAt': attempted, 'changed': changed}
                source_results.append({'name': name + (' · 页面有变化，请人工核实' if changed else ' · 已记录页面指纹'), 'url': url, 'status': 'ok', 'count': 0})
                successes += 1
            except (urllib.error.URLError, OSError, ValueError) as exc:
                source_results.append({'name': name, 'url': url, 'status': 'error', 'error': str(exc)[:220]})
        try:
            candidates, discovery_errors = official_candidates()
            count = 0
            for title, body, url, published_at in candidates:
                for entry in summarize_official(title, body, url, published_at, attempted):
                    previous = briefs.get(entry['id'])
                    if not previous or (entry.get('publishedAt') or '') >= (previous.get('publishedAt') or ''):
                        briefs[entry['id']] = entry
                    count += 1
            official_status = 'partial' if discovery_errors else 'ok'
            last_official_success = attempted
            successes += 1
            source_results.append({'name': '首尔官方活动中文简报', 'url': OFFICIAL_FEED,
                                   'status': official_status, 'count': count, 'errors': discovery_errors})
        except (urllib.error.URLError, OSError, ET.ParseError, ValueError) as exc:
            official_status = 'error'
            source_results.append({'name': '首尔官方活动中文简报', 'url': OFFICIAL_FEED,
                                   'status': 'error', 'error': str(exc)[:220]})
        try:
            observed_rates = hotel_rates(read(HOTEL_URL), attempted)
            hotel_status = 'ok'
            successes += 1
            source_results.append({'name': 'Trip.com 所选日期酒店双床房列表快照（非订单确认）', 'url': HOTEL_URL, 'status': 'ok', 'count': len(observed_rates)})
        except (urllib.error.URLError, OSError, ValueError) as exc:
            hotel_status = 'error'
            source_results.append({'name': 'Trip.com 所选日期酒店双床房列表快照', 'url': HOTEL_URL, 'status': 'error', 'error': str(exc)[:220]})
    total = len(SOURCES) + (0 if fixture else len(OFFICIAL) + 2)
    result = {
        'status': 'ok' if successes == total and all(s['status'] == 'ok' for s in source_results) else 'partial' if successes else 'error',
        'lastAttempt': attempted, 'lastSuccess': attempted if successes else prior.get('lastSuccess'),
        'schedule': '每日北京时间 09:00 / 首尔 10:00（GitHub Actions 可能延迟）',
        'items': sorted(items.values(), key=lambda item: item.get('publishedAt') or item['discoveredAt'], reverse=True)[:40],
        'sources': source_results, 'officialPages': official_pages,
        'eventBriefs': list(briefs.values()), 'officialStatus': official_status,
        'lastOfficialSuccess': last_official_success,
        'observedHotelRates': observed_rates,
        'priceMonitoring': {'status': 'hotel_list_observation_only', 'flights': 'disabled_by_user', 'hotels': hotel_status,
                            'hotelDates': ['2026-12-31', '2027-01-03'], 'adults': 2, 'rooms': 1,
                            'hotelNightlyBudgetCNY': 2000},
        'note': '活动页只展示有本季完整日期的首尔官方公告中文卡片；原始检索线索不在页面列出。酒店只观察三晚双床房列表含税总价；机票按用户截图整理，停止联网查价。来源失败时保留原时间的已有信息。'
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(output)
    print(f'Monitor: {result["status"]}; {successes}/{total} sources; {len(result["items"])} retained leads')
    return 0 if successes else 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=pathlib.Path, default=ROOT / 'public' / 'updates.json')
    parser.add_argument('--fixture', help='Offline RSS fixture for parser validation only')
    args = parser.parse_args()
    raise SystemExit(collect(args.output, args.fixture))
