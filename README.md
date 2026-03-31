# 🎬 ANIWATCH/MEGACLOUD EXTRACTOR

## ⚠️ IMPORTANT CREDITS & SOURCES ⚠️

This project is possible because of these amazing open-source projects:

---

### 🏆 PRIMARY REFERENCE - yt-dlp HIANIME PLUGIN

**yt-dlp hianime plugin** by @pratikpatel8982
- GitHub: https://github.com/pratikpatel8982/yt-dlp-hianime
- This project ported the megacloud extraction logic from here!
- Stars: 37+ | Language: Python

**yt-dlp** (The video downloader framework)
- GitHub: https://github.com/yt-dlp/yt-dlp
- 150K+ stars, the best video downloader ever!
- Stars: 150K+ | Language: Python

**yt-dlp contributors:**
- @candrapersada - Co-maintainer
- All open-source contributors

---

### 📚 PYTHON LIBRARIES

**curl_cffi** - TLS fingerprint bypass for Cloudflare
- GitHub: https://github.com/YSievert/curl_cffi
- Impersonates Chrome/Firefox TLS fingerprints
- pip: `pip install curl_cffi`

**requests** - HTTP library for Python
- GitHub: https://github.com/psf/requests
- pip: `pip install requests`

---

### 🌐 ALTERNATIVE APIS DISCOVERED

**AnimeKAI + enc-dec.app** (Working Alternative)
- AnimeKAI: https://anikai.to
- Encryption API: https://enc-dec.app
- No Cloudflare protection - easier to access

**MegaPlay API** (Reference)
- Documentation: https://megaplay.buzz/api
- Used for understanding MegaCloud endpoints

---

### 🔗 OTHER PROJECTS THAT HELPED

**hianime-api** by @ryanwtf88
- GitHub: https://github.com/ryanwtf88/hianime-api
- Comprehensive HiAnime scraping API

**Miruro-API** by @walterwhite-69
- GitHub: https://github.com/walterwhite-69/Miruro-API
- Miruro streaming API

**AnimeKAI-API** by @walterwhite-69
- GitHub: https://github.com/walterwhite-69/AnimeKAI-API
- AnimeKai REST API

---

### 📡 SOURCE SITES

- **aniwatchtv.to** - Anime streaming site (uses MegaCloud player)
- **megacloud.blog** - Video player/CDN provider
- **hianimez.to** - Alternative domain
- **anikai.to** - Alternative anime site

---

### 🔧 TOOLS USED

- **Chrome DevTools** - Network analysis for API discovery
- **Regex101** - Testing regular expressions
- **GitHub** - Code reference and collaboration

---

## 📜 LICENSE

This project is for **EDUCATIONAL PURPOSES ONLY**.

The original yt-dlp plugin is released under The Unlicense.
Please respect the content creators and streaming services.

---

## 🚀 QUICK START

```bash
# 1. Install dependencies
pip install curl_cffi requests

# 2. Run extractor
python3 aniwatch_extractor.py <anime-slug> <episode>

# Examples:
python3 aniwatch_extractor.py monster-37 1
python3 aniwatch_extractor.py death-note-60 1
python3 aniwatch_extractor.py code-geass-lelouch-of-the-rebellion-r2-17 1
```

---

## 📁 FILES

| File | Purpose |
|------|---------|
| `aniwatch_extractor.py` | Main CLI Extractor |
| `megacloud_extractor.py` | JavaScript Deobfuscation Core |
| `api.py` | REST API Server |
| `worker.js` | Cloudflare Workers Version |
| `HACKING_SUMMARY.md` | Complete Guide with Diagrams |

---

## 🔑 HOW IT WORKS

1. **Cloudflare Bypass** - Uses curl_cffi to impersonate Chrome browser
2. **API Discovery** - Network analysis found hidden `/getSources` endpoint
3. **JS Deobfuscation** - Replicated MegaCloud's obfuscated JavaScript logic
4. **M3U8 Extraction** - Got the 1080p video URL! 🎉

---

## ⚠️ DISCLAIMER

- URLs expire quickly - extract fresh each time
- For educational purposes only
- Support original creators by watching on official platforms

---

**Created by: V6.6.1 Project**
**Based on: yt-dlp hianime plugin**

**Last Updated: March 31, 2026**
