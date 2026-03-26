#!/usr/bin/env python3
"""Standalone scraper test to run outside Kodi.
Fetches the whats-on-now page and prints found schedules and direct video links.
"""
import urllib.request
import urllib.parse
import re

BASE_URL = 'https://www.churchservices.tv'
UA = 'Mozilla/5.0 (X11; Linux x86_64)'

def get_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='replace')

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text).strip()

def main():
    html = get_url(BASE_URL + '/whats-on-now/')
    pattern = re.compile(
        r'<div class="row row-striped click-schedule"[^>]*data-href="(?P<href>[^"]+)"[^>]*>.*?'
        r'<div class="church-daily-schedule-time[^\"]*"[^>]*data-src="(?P<time>[^"]+)"[^>]*>.*?</div>.*?'
        r'<div class="church-daily-schedule-title schedule-record">(?P<title>.*?)</div>.*?'
        r'<div class="church-daily-schedule-title">(?P<church>.*?)</div>',
        re.S
    )

    for m in pattern.finditer(html):
        href = m.group('href').strip()
        time = clean_html(m.group('time'))
        title = clean_html(m.group('title'))
        church = clean_html(m.group('church'))
        print(f"{time} - {title} - {church} - {href}")
        page = get_url(urllib.parse.urljoin(BASE_URL, href))
        # poster from <video poster=>
        vp = re.search(r'<video[^>]*poster=["\']([^"\']+)["\']', page)
        if vp:
            print('  poster:', urllib.parse.urljoin(BASE_URL, vp.group(1)))
        mm = re.search(r'<div[^>]*class=["\']default-stream["\'][^>]*data-src=["\']([^"\']+)["\']', page)
        if mm:
            print('  video:', mm.group(1))
        else:
            mm2 = re.search(r'(https?://[^"\']+?\.m3u8)', page)
            if mm2:
                print('  video:', mm2.group(1))
            else:
                print('  no video found')

if __name__ == '__main__':
    main()
