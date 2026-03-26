#!/usr/bin/env python3
# Kodi plugin: ChurchServices
import sys
import re
import urllib.request
import urllib.parse
import os
import hashlib
import html as html_lib

try:
    import xbmc
    import xbmcgui
    import xbmcplugin
except Exception:
    xbmc = xbmcgui = xbmcplugin = None

HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else 0
ADDON_URL = sys.argv[0]
ARGS = sys.argv[2][1:] if len(sys.argv) > 2 else ''
PARAMS = dict((k, v[0]) for k, v in urllib.parse.parse_qs(ARGS).items())

BASE_URL = 'https://www.churchservices.tv'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64)'

def cache_thumb(url):
    """If running inside Kodi, download remote thumbnail to addon data cache and return local path.
    Otherwise return the original url."""
    if not xbmc or not url:
        return url
    try:
        # only handle http(s) or protocol-relative URLs
        if url.startswith('//'):
            url = 'https:' + url
        if not url.startswith('http'):
            return url
        cache_dir = translate_path('special://profile/addon_data/plugin.video.churchservices/thumbs')
        cache_dir = os.path.normpath(cache_dir)
        os.makedirs(cache_dir, exist_ok=True)
        path = urllib.parse.urlparse(url).path
        ext = os.path.splitext(path)[1] or '.jpg'
        name = hashlib.md5(url.encode('utf-8')).hexdigest() + ext
        local = os.path.join(cache_dir, name)
        if not os.path.exists(local) or os.path.getsize(local) == 0:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            with open(local, 'wb') as fh:
                fh.write(data)
        return local
    except Exception:
        return url


def kodi_log(msg, level=None):
    try:
        if xbmc:
            xbmc.log('ChurchServices: %s' % msg, level if level is not None else xbmc.LOGDEBUG)
    except Exception:
        pass


def make_art_uri(url):
    """Resolve a remote thumbnail URL into a Kodi-friendly art URI.

    Primary approach: cache locally (in kodi addon_data) and use file:// URI for best performance.
    Fallback: if caching fails, use the remote URL directly.
    """
    if not url:
        return None
    if url.startswith('//'):
        url = 'https:' + url
    if not re.match(r'^https?://', url):
        url = urllib.parse.urljoin(BASE_URL, url)

    kodi_log('make_art_uri resolving %s' % url)

    maybe_local = cache_thumb(url)

    # If caching returned a local file path, prefer returning the absolute path
    # (Kodi handles absolute filesystem paths well on LibreELEC). Use xbmcvfs.exists
    # when available to ensure Kodi can access the file.
    try:
        if maybe_local and os.path.isabs(maybe_local) and os.path.exists(maybe_local):
            try:
                import xbmcvfs
                if xbmcvfs.exists(maybe_local):
                    kodi_log('make_art_uri using cached file (xbmcvfs) %s' % maybe_local)
                    return maybe_local
            except Exception:
                # fall back to plain filesystem check
                kodi_log('make_art_uri using cached file %s' % maybe_local)
                return maybe_local
    except Exception:
        pass

    # cache_thumb may return a remote URL or local path; ensure remote fallback works
    if maybe_local and re.match(r'^https?://', maybe_local):
        kodi_log('make_art_uri using remote url fallback %s' % maybe_local)
        return maybe_local

    kodi_log('make_art_uri raw url fallback %s' % url)
    if re.match(r'^https?://', url):
        return url

    kodi_log('make_art_uri failed to resolve %s' % url)
    return None


def make_placeholder(path):
    """Create a tiny placeholder PNG at path if it doesn't exist."""
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path
        import base64
        placeholder_b64 = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=='
        placeholder_png = base64.b64decode(placeholder_b64)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as fh:
            fh.write(placeholder_png)
        return path
    except Exception:
        return None


def translate_path(path):
    """Translate Kodi special:// paths to real filesystem paths safely.

    Tries xbmc.translatePath first; falls back to xbmcaddon.Addon().getAddonInfo('profile')
    for addon_data paths, and finally to a sensible ~/.kodi fallback.
    """
    try:
        if xbmc and hasattr(xbmc, 'translatePath'):
            return xbmc.translatePath(path)
    except Exception:
        pass

    # Handle addon profile paths using xbmcaddon if available
    try:
        import xbmcaddon
        addon = xbmcaddon.Addon()
        if path.startswith('special://profile/addon_data'):
            rest = path[len('special://profile/addon_data'):]
            profile = addon.getAddonInfo('profile')
            return os.path.normpath(profile + rest.replace('/', os.sep))
        if path.startswith('special://profile'):
            rest = path[len('special://profile'):]
            profile = addon.getAddonInfo('profile')
            return os.path.normpath(profile + rest.replace('/', os.sep))
    except Exception:
        pass

    # Generic fallback: map special://profile to ~/.kodi
    if path.startswith('special://profile'):
        rest = path[len('special://profile'):]
        return os.path.expanduser('~/.kodi') + rest.replace('/', os.sep)

    return path

def get_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode('utf-8', errors='replace')

def make_plugin_url(**kwargs):
    return ADDON_URL + '?' + urllib.parse.urlencode(kwargs)

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text).strip()


def extract_page_poster(page_html):
    """Find a poster/image URL on a livestream page.

    Tries, in order:
    - any `poster=` attribute (quoted or unquoted)
    - common `data-` poster/thumb attributes
    - inline `background-image: url(...)`
    - `<meta property="og:image">` and common alternatives
    - `<link rel="image_src">`
    - first `<img src=...>`

    Returns an absolute URL or None.
    """
    try:
        if not page_html:
            return None

        def _norm(u):
            if not u:
                return None
            u = html_lib.unescape(u).strip()
            if u.startswith('//'):
                return 'https:' + u
            if not re.match(r'^https?://', u):
                return urllib.parse.urljoin(BASE_URL, u)
            return u

        # 1) poster attribute anywhere
        m = re.search(r'poster\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^>\s]+))', page_html, re.I)
        if m:
            url = m.group(1) or m.group(2) or m.group(3)
            return _norm(url)

        # 2) data-* attributes often used for thumbnails
        m = re.search(r'\b(?:data-poster|data-thumb|data-thumbnail|data-image|data-src-poster)\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^>\s]+))', page_html, re.I)
        if m:
            url = m.group(1) or m.group(2) or m.group(3)
            return _norm(url)

        # 3) background-image: url(...)
        m = re.search(r'background(?:-image)?\s*:\s*url\((?:"|\')?(?P<u>[^"\')]+)(?:"|\')?\)', page_html, re.I)
        if m:
            return _norm(m.group('u'))

        # 4) OpenGraph / Twitter image
        m = re.search(r'<meta[^>]*(?:property|name)=["\'](?:og:image|twitter:image|twitter:image:src)["\'][^>]*content=["\']([^"\']+)["\']', page_html, re.I)
        if m:
            return _norm(m.group(1))

        # 5) link rel=image_src
        m = re.search(r'<link[^>]*rel=["\']image_src["\'][^>]*href=["\']([^"\']+)["\']', page_html, re.I)
        if m:
            return _norm(m.group(1))

        # 6) first img src
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', page_html, re.I)
        if m:
            return _norm(m.group(1))
    except Exception:
        pass
    return None


def parse_schedule(html):
    """Parse whats-on-now HTML and return list of dicts with href,time,title,church."""
    block_pattern = re.compile(
        r'<div\b[^>]*\bclass=["\'](?=[^"\']*\brow\b)(?=[^"\']*\brow-striped\b)(?=[^"\']*\bclick-schedule\b)[^"\']*["\'][^>]*\bdata-href=["\']([^"\']+)["\'][^>]*>(.*?)(?=<div\b[^>]*\bclass=["\'](?=[^"\']*\brow\b)(?=[^"\']*\brow-striped\b)(?=[^"\']*\bclick-schedule\b)[^"\']*["\']|$)',
        re.S | re.I
    )

    blocks = block_pattern.findall(html)
    results = []
    if not blocks:
        return results

    time_re = re.compile(
        r'<[^>]*\bclass=["\'][^"\']*\bchurch-daily-schedule-time\b[^"\']*["\'][^>]*\bdata-src=["\']([^"\']+)["\']',
        re.S | re.I
    )

    title_re = re.compile(
        r'<div[^>]*\bclass=["\']church-daily-schedule-title(?:\s+schedule-record)?["\'][^>]*>(.*?)</div>',
        re.S | re.I
    )

    for href, block in blocks:
        try:
            time_m = time_re.search(block)
            title_divs = title_re.findall(block)
            if not (time_m and title_divs and len(title_divs) >= 2):
                time_alt = re.search(r'data-src=["\']([^"\']+)["\']', block)
                time = clean_html(time_alt.group(1)) if time_alt else ''
                title = clean_html(title_divs[0]) if title_divs else ''
                church = clean_html(title_divs[-1]) if title_divs else ''
            else:
                time = clean_html(time_m.group(1))
                title = clean_html(title_divs[0])
                church = clean_html(title_divs[-1])

            results.append({'href': href, 'time': time, 'title': title, 'church': church})
        except Exception:
            continue

    return results

def list_streams():
    try:
        html = get_url(BASE_URL + '/whats-on-now/')
    except Exception as e:
        if xbmcgui:
            xbmcgui.Dialog().ok('ChurchServices', 'Failed to load whats-on-now: %s' % e)
        return

    # Parse schedule blocks using helper (falls back like scrape_live)
    parsed = parse_schedule(html)
    if not parsed:
        if xbmcgui:
            xbmcgui.Dialog().ok('ChurchServices', 'No current streams found.')
        return

    if xbmcplugin:
        try:
            xbmcplugin.setContent(HANDLE, 'movies')
        except Exception:
            try:
                xbmcplugin.setContent(HANDLE, 'videos')
            except Exception:
                pass

    for entry in parsed:
        href = entry.get('href')
        time = entry.get('time', '')
        title = entry.get('title', '')
        church = entry.get('church', '')
        label = f"{time} — {title} — {church}"

        # try to extract a thumbnail from the church page: prefer <video poster=>, then og:image, then first img
        thumb = ''
        try:
            page_html = get_url(urllib.parse.urljoin(BASE_URL, href))
            poster_url = extract_page_poster(page_html)
            if poster_url:
                thumb = poster_url
            else:
                thumb = ''
        except Exception:
            thumb = ''

        li = xbmcgui.ListItem(label=label) if xbmcgui else None
        if li:
            li.setInfo('video', {'title': label, 'plot': church})
            li.setProperty('IsPlayable', 'true')
            if thumb:
                art_uri = make_art_uri(thumb)
                if not art_uri:
                    # fallback to safe placeholder if image failed to resolve
                    placeholder = os.path.join(translate_path('special://profile/addon_data/plugin.video.churchservices/thumbs'), 'placeholder.png') if xbmc else None
                    ph = make_placeholder(placeholder) if placeholder else None
                    if ph:
                        art_uri = ph

                if art_uri:
                    li.setArt({
                        'thumb': art_uri,
                        'icon': art_uri,
                        'fanart': art_uri,
                        'poster': art_uri,
                        'banner': art_uri
                    })
                    try:
                        li.setProperty('fanart_image', art_uri)
                    except Exception:
                        pass

                kodi_log('list_streams: set material %s -> %s' % (label, art_uri))

        url = make_plugin_url(mode='play', href=href, title=label)
        if xbmcplugin:
            xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=False)

    if xbmcplugin:
        xbmcplugin.endOfDirectory(HANDLE)

def play_stream(href, title=''):
    if not href:
        if xbmcgui:
            xbmcgui.Dialog().ok('ChurchServices', 'No stream href provided')
        return
    try:
        page_html = get_url(urllib.parse.urljoin(BASE_URL, href))
    except Exception as e:
        if xbmcgui:
            xbmcgui.Dialog().ok('ChurchServices', 'Failed to load page: %s' % e)
        return

    m = re.search(r'<div[^>]*class=["\']default-stream["\'][^>]*data-src=["\']([^"\']+)["\']', page_html)
    if m:
        video_url = m.group(1)
    else:
        # fallback: first .m3u8 URL on the page
        m2 = re.search(r'(https?://[^"\']+?\.m3u8)', page_html)
        if m2:
            video_url = m2.group(1)
        else:
            if xbmcgui:
                xbmcgui.Dialog().ok('ChurchServices', 'No stream URL found on the page')
            return

    # try to get a poster for the player
    poster = None
    try:
        poster = extract_page_poster(page_html)
    except Exception:
        poster = None

    li = xbmcgui.ListItem(path=video_url) if xbmcgui else None
    if li and xbmcplugin:
        if title:
            li.setInfo('video', {'title': title})
        if poster:
            poster_uri = make_art_uri(poster)
            if not poster_uri:
                placeholder = os.path.join(translate_path('special://profile/addon_data/plugin.video.churchservices/thumbs'), 'placeholder.png') if xbmc else None
                ph = make_placeholder(placeholder) if placeholder else None
                if ph:
                    poster_uri = 'file://' + ph if not ph.startswith('file://') else ph

                if poster_uri:
                    li.setArt({
                        'thumb': poster_uri,
                        'icon': poster_uri,
                        'fanart': poster_uri,
                        'poster': poster_uri,
                        'banner': poster_uri
                    })
            kodi_log('play_stream: set resolved art for "%s": %s' % (title, poster_uri))
        xbmcplugin.setResolvedUrl(HANDLE, True, li)

def router():
    mode = PARAMS.get('mode')
    if mode == 'play':
        play_stream(PARAMS.get('href'), PARAMS.get('title', ''))
    else:
        list_streams()

if __name__ == '__main__':
    router()
