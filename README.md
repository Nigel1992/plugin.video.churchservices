[![Discord](https://img.shields.io/discord/1468295714961494029?color=7289da&label=Join%20Our%20Discord&logo=discord&logoColor=white&style=for-the-badge)](https://discord.gg/9F2NZuydXT)


![ChurchServices](icon.png)

# ChurchServices — Kodi Add-on

[![Vibe Coded](https://img.shields.io/badge/Vibe_Coded-✨-8A2BE2?style=for-the-badge)](https://github.com)

>A lightweight Kodi video add-on that lists live streams from the "What's On Now" page on churchservices.tv and plays direct HLS (m3u8) streams.

• [Get latest release](https://github.com/Nigel1992/plugin.video.churchservices/releases/latest) 
• [Issues](https://github.com/Nigel1992/plugin.video.churchservices/issues)

## Features

- Scrapes the live schedule from churchservices.tv and shows currently streaming services.
- Resolves direct HLS (.m3u8) links for playback in Kodi.
- Fetches thumbnails/posters when available and caches them for smoother UI.
- Minimal, dependency-free Python code designed to run inside Kodi.

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

## 💖 Support the Project

I build this project in my free time and don't need donations for myself. If you'd like to give something back, I'd kindly ask you to donate to a charity of your choice instead — they need it far more than I do. If you still prefer to support me directly in private, thank you so much; it's genuinely appreciated, and I'll be happy to list you as a donor on GitHub and, where applicable, in a donors section of the project, as a small thank you.

[![Ko-Fi](https://img.shields.io/badge/Ko--Fi-Support%20me-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/nigel1992)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=KYV9ARF99ZSCE)
