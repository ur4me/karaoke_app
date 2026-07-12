# 🎤 STEVE KARAOKE

A self-hosted karaoke web app that searches, queues, and continuously plays YouTube karaoke videos.
When a song ends, a 100-point celebration screen and fanfare play for 3 seconds before automatically moving on to the next song.

Runs on the Python standard library only — no external packages required.

## ✨ Features

- **Search & Reserve**: Type an artist or song title to search YouTube karaoke videos and add them to the queue (the keyword "노래방" / karaoke is appended automatically)
- **Queue Management**: Reorder songs with drag and drop, or cancel individual songs
- **Auto Continuous Play**: When a song ends, the 100-point screen (3 seconds) + fanfare play, then the next song starts automatically
- **Skip**: Jump to the next song while one is playing
- **Fullscreen Mode**: Use the ⛶ button at the bottom right of the app
  - ⚠️ The YouTube player's own fullscreen button is disabled, because it would cover the score screen. Always use the app's fullscreen button instead.

## 📁 Project Files

| File | Description |
|---|---|
| `steve_karaoke_render.py` | Main app (server + frontend, works both locally and on Render) |
| `image_d05c44.jpg` | 100-point celebration image shown when a song ends |
| `fanfare.mp3` | Fanfare sound effect played with the score screen |
| `requirements.txt` | Empty file (standard library only; needed for Render's build step) |

> The app still works even if `image_d05c44.jpg` or `fanfare.mp3` is missing. Without the image, a neon-styled fallback screen ("100 PERFECT SCORE!") is shown instead, and a warning is printed to the terminal at server startup.

## 🖥️ Running Locally

Requirements: Python 3.8+

```bash
cd <project folder>
python3 steve_karaoke_render.py
```

Your browser will automatically open `http://localhost:8080`.

- To use a different port: `PORT=9090 python3 steve_karaoke_render.py`
- If you get an `Address already in use` error, stop the previously running server with Ctrl+C and run it again.

## ☁️ Deploying to Render

1. Push this repository to GitHub (including all four files above).
2. On [Render](https://render.com), create a **New → Web Service** and connect the repository.
3. Configure:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt` (default is fine)
   - **Start Command**: `python steve_karaoke_render.py`
4. Once deployed, open the URL Render provides.

The app automatically binds to the `PORT` environment variable set by Render, and skips opening a browser when the `RENDER` environment variable is detected.

## ⚠️ Known Limitations

- **YouTube search may be blocked**: Search works by scraping the YouTube search results page. From datacenter IPs (such as Render's), YouTube may block requests, leaving search results empty. In that case, the search logic needs to be replaced with the official YouTube Data API.
- **Some videos won't play**: Karaoke videos whose uploaders have disabled external embedding cannot be played in the player.
- **No queue sharing between devices**: The queue lives only inside each browser. Multiple devices visiting the same URL each get their own independent karaoke session — "reserve on your phone, play on the TV" is not supported.
- **First fanfare playback**: Due to browser autoplay policies, at least one click on the page (search, reserve, etc.) is required before the fanfare sound can play. In normal usage this unlocks naturally.

## 🛠️ Tech Stack

- **Backend**: Python standard library (`http.server`, multithreaded `socketserver`) — zero external dependencies
- **Frontend**: Single-page vanilla HTML/CSS/JS with the YouTube IFrame Player API
- **Search**: Scraping of YouTube search result pages (regex parsing)

## 📄 License

Free for personal use. When using YouTube content, please comply with the YouTube Terms of Service.
