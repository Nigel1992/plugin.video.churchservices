![ChurchServices](icon.png)

# ChurchServices — Kodi Add-on

>A lightweight Kodi video add-on that lists live streams from the "What's On Now" page on churchservices.tv and plays direct HLS (m3u8) streams.

[Release 0.1.0](https://github.com/Nigel1992/plugin.video.churchservices/releases/tag/0.1.0) • [Issues](https://github.com/Nigel1992/plugin.video.churchservices/issues)

## Features

- Scrapes the live schedule from churchservices.tv and shows currently streaming services.
- Resolves direct HLS (.m3u8) links for playback in Kodi.
- Fetches thumbnails/posters when available and caches them for smoother UI.
- Minimal, dependency-free Python code designed to run inside Kodi.
- Includes `scrape_test.py` — a standalone scraper for quick local testing.

## Installation

### From Releases (recommended)

1. Download `plugin.video.churchservices.zip` from the Releases page.
2. In Kodi: Add-ons → Install from zip file → select the downloaded ZIP.

### From Source (developer)

```bash
git clone https://github.com/Nigel1992/plugin.video.churchservices.git
cp -r plugin.video.churchservices ~/.kodi/addons/
# Restart Kodi
```

## Usage

- Open Kodi → Add-ons → Video Add-ons → ChurchServices.
- Select any listing to start playback. The add-on resolves and hands the HLS stream to Kodi's player.

## Development & Testing

- Run the standalone scraper locally to inspect what the add-on will find:

```bash
python3 scrape_test.py
```

This script uses only the Python standard library (urllib + regex) and prints schedule entries, posters, and resolved stream URLs.

## Contributing

- Contributions welcome — open issues and PRs. For larger changes, please open an issue first to discuss.

## License

- No license specified. If you want this project to be reusable, consider adding a `LICENSE` (for example, MIT).

## Contact & Links

- Website: https://www.churchservices.tv
- Repository: https://github.com/Nigel1992/plugin.video.churchservices

