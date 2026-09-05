![ChurchServices](icon.png)

# ChurchServices — Kodi Add-on

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

All donations go towards your chosen charity. You can pick any charity you'd like, and 5% is retained due to Ko-Fi fees. As a thank you, your name will be listed as a supporter/donor in a GitHub project. Feel free to email me at thedjskywalker@gmail.com for proof! :)

[![Ko-Fi](https://img.shields.io/badge/Ko--Fi-Support%20me-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/nigel1992)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=KYV9ARF99ZSCE)

---

## Contributing

- Contributions welcome — open issues and PRs. For larger changes, please open an issue first to discuss.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

MIT © 2026 Nigel1992

## Contact & Links

- Website: https://www.churchservices.tv
- Repository: https://github.com/Nigel1992/plugin.video.churchservices

