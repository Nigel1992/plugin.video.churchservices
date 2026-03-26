# ChurchServices Kodi Addon

This Kodi addon scrapes https://www.churchservices.tv/whats-on-now/ and lists current live streams. Selecting an item resolves the direct HLS (m3u8) stream and starts playback.

Installation:
- Copy the `plugin.video.churchservices` folder to your Kodi `addons` directory and restart Kodi, or zip the folder and install from the Kodi addon browser.

Notes:
- The addon uses simple HTML scraping; it may need updates if the site layout changes.
- Thumbnails are taken from the church page when available (og:image or first image on the page).
