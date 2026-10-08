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
    ('COUNTDOWN FANTASY / HYUKOH', 'COUNTDOWN FANTASY (2026 OR 2027) (HYUKOH OR 혁오)'),
    ('카운트다운 판타지', '카운트다운 판타지 (2026 OR 2027)'),
    ('首尔官方跨年线索', '서울 2026 2027 제야의 종 보신각'),
]
OFFICIAL = [('MINT PAPER 主办方首页变化（不等于当届公告）', 'https://www.mintpaper.co.kr/'),
            ('首尔市英文首页变化（不等于跨年公告）', 'https://english.seoul.go.kr/'),
            ('NOL 当届票务页变化（可能含倒计时等动态变化）', 'https://nol.yanolja.com/ticket/products/26014480')]
HOTEL_URL = 'https://www.trip.com/hotels/list?city=274&checkin=2026-12-31&checkout=2027-01-03&adult=2&crn=1&curr=CNY'

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, value):
        if value.strip():
            self.parts.append(value.strip())

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
            observed_rates = hotel_rates(read(HOTEL_URL), attempted)
            hotel_status = 'ok'
            successes += 1
            source_results.append({'name': 'Trip.com 所选日期酒店双床房列表快照（非订单确认）', 'url': HOTEL_URL, 'status': 'ok', 'count': len(observed_rates)})
        except (urllib.error.URLError, OSError, ValueError) as exc:
            hotel_status = 'error'
            source_results.append({'name': 'Trip.com 所选日期酒店双床房列表快照', 'url': HOTEL_URL, 'status': 'error', 'error': str(exc)[:220]})
    total = len(SOURCES) + (0 if fixture else len(OFFICIAL) + 1)
    result = {
        'status': 'ok' if successes == total else 'partial' if successes else 'error',
        'lastAttempt': attempted, 'lastSuccess': attempted if successes else prior.get('lastSuccess'),
        'schedule': '每日北京时间 09:00 / 首尔 10:00（GitHub Actions 可能延迟）',
        'items': sorted(items.values(), key=lambda item: item.get('publishedAt') or item['discoveredAt'], reverse=True)[:40],
        'sources': source_results, 'officialPages': official_pages,
        'observedHotelRates': observed_rates,
        'priceMonitoring': {'status': 'hotel_list_observation_only', 'flights': 'not_connected', 'hotels': hotel_status, 'flightDates': ['2026-12-31', '2027-01-03'],
                            'hotelDates': ['2026-12-31', '2027-01-03'], 'adults': 2, 'rooms': 1,
                            'hotelNightlyBudgetCNY': 2000},
        'note': '新闻线索和官方首页变化需人工核实。酒店仅采集所选日期、两人一间双床房的列表含税总价，非订单库存保证；机票报价尚未接入。来源失败时保留旧快照，必须查看每条查价时间。'
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
