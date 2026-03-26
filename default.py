#!/usr/bin/env python3
# Kodi plugin: ChurchServices
import sys
import re
import urllib.request
import urllib.parse
import os
import hashlib

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

    if maybe_local and os.path.isfile(maybe_local):
        uri = 'file:///' + maybe_local.replace('\\', '/') if os.name == 'nt' else 'file://' + maybe_local
        kodi_log('make_art_uri using cached file %s' % uri)
        return uri

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

def list_streams():
    try:
        html = get_url(BASE_URL + '/whats-on-now/')
    except Exception as e:
        if xbmcgui:
            xbmcgui.Dialog().ok('ChurchServices', 'Failed to load whats-on-now: %s' % e)
        return

    pattern = re.compile(
        r'<div class="row row-striped click-schedule"[^>]*data-href="(?P<href>[^"]+)"[^>]*>.*?'
        r'<div class="church-daily-schedule-time[^\"]*"[^>]*data-src="(?P<time>[^"]+)"[^>]*>.*?</div>.*?'
        r'<div class="church-daily-schedule-title schedule-record">(?P<title>.*?)</div>.*?'
        r'<div class="church-daily-schedule-title">(?P<church>.*?)</div>',
        re.S
    )

    matches = list(pattern.finditer(html))
    if not matches:
        if xbmcgui:
            xbmcgui.Dialog().ok('ChurchServices', 'No current streams found.')
        return

    # hint Kodi that this directory contains movies (helps skins pick artwork/poster view)
    if xbmcplugin:
        try:
            xbmcplugin.setContent(HANDLE, 'movies')
        except Exception:
            try:
                xbmcplugin.setContent(HANDLE, 'videos')
            except Exception:
                pass

    for m in matches:
        href = m.group('href').strip()
        time = clean_html(m.group('time'))
        title = clean_html(m.group('title'))
        church = clean_html(m.group('church'))
        label = f"{time} — {title} — {church}"

        # try to extract a thumbnail from the church page: prefer <video poster=>, then og:image, then first img
        thumb = ''
        try:
            page_html = get_url(urllib.parse.urljoin(BASE_URL, href))
            vposter = re.search(r'<video[^>]*poster=["\']([^"\']+)["\']', page_html)
            if vposter:
                thumb = vposter.group(1)
            else:
                og = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', page_html)
                if og:
                    thumb = og.group(1)
                else:
                    img = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', page_html)
                    if img:
                        thumb = img.group(1)
            # normalize scheme-less and relative URLs
            if thumb:
                if thumb.startswith('//'):
                    thumb = 'https:' + thumb
                elif not re.match(r'^https?://', thumb):
                    thumb = urllib.parse.urljoin(BASE_URL, thumb)
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
                        art_uri = 'file://' + ph if not ph.startswith('file://') else ph

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
        vp = re.search(r'<video[^>]*poster=["\']([^"\']+)["\']', page_html)
        if vp:
            poster = vp.group(1)
            if poster.startswith('//'):
                poster = 'https:' + poster
            elif not re.match(r'^https?://', poster):
                poster = urllib.parse.urljoin(BASE_URL, poster)
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
