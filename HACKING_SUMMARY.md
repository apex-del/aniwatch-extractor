# MEGACLOUD HACKING - COMPLETE SUMMARY V6.6.1

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

**How to find slug:** Go to aniwatchtv.to → Search anime → Copy slug from URL

---

## 🎯 THE GOAL

Extract M3U8 streaming URLs from aniwatchtv.to which uses MegaCloud player.

---

## 🔄 THE COMPLETE FLOW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ANIWATCH MEGACLOUD HACK                          │
└─────────────────────────────────────────────────────────────────────────────┘

    USER                          BROWSER                           MEGACLOUD
      │                              │                                  │
      │  1. Open aniwatchtv.to       │                                  │
      │─────────────────────────────▶│                                  │
      │                              │                                  │
      │  2. Click Episode            │                                  │
      │─────────────────────────────▶│                                  │
      │                              │                                  │
      │                              │  3. Load MegaCloud Player         │
      │                              │─────────────────────────────────▶│
      │                              │                                  │
      │                              │  4. Get obfuscated JS           │
      │                              │◀─────────────────────────────────│
      │                              │                                  │
      │  5. Show Video Player        │                                  │
      │◀─────────────────────────────│                                  │
      │                              │                                  │
      │                              │  6. Hidden API call:              │
      │                              │     /getSources?id=ID&_k=KEY     │
      │                              │─────────────────────────────────▶│
      │                              │                                  │
      │                              │  7. Return encrypted M3U8        │
      │                              │◀─────────────────────────────────│
      │                              │                                  │
      │  8. PLAY VIDEO!              │                                  │
      │◀─────────────────────────────│                                  │
      │                              │                                  │
      │                              │                                  │
      ▼                              ▼                                  ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                         OUR PYTHON EXTRACTOR                                │
│                                                                             │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐       │
│   │ Step 1   │────▶│ Step 2   │────▶│ Step 3   │────▶│ Step 4   │       │
│   │ Episode  │     │ Get      │     │ Get      │     │ Extract  │       │
│   │ ID       │     │ Servers  │     │ Embed    │     │ M3U8     │       │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘       │
│        │                │                │                │               │
│        ▼                ▼                ▼                ▼               │
│   aniwatchtv.to   aniwatchtv.to   megacloud.blog   megacloud.blog      │
│   /ajax/v2/       /ajax/v2/       /embed-2/       /getSources         │
│   episode/list    episode/servers  v3/e-1/ID       + Deobfuscation       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              V6.6.1 SYSTEM                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│        CLIENTS                  │      │        API SERVER              │
│                                 │      │                                 │
│  ┌─────────┐  ┌─────────┐     │      │  ┌─────────────────────────┐     │
│  │  CLI    │  │ Android │     │      │  │   curl_cffi Bypass    │     │
│  │ Python  │  │   App   │     │      │  │   ┌─────────────────┐  │     │
│  └────┬────┘  └────┬────┘     │      │  │   │ Cloudflare     │  │     │
│       │            │           │      │  │   │ Bypass ✅      │  │     │
│       └──────┬─────┘           │      │  │   └─────────────────┘  │     │
│              │                 │      │  │          │              │     │
│              ▼                 │      │  │          ▼              │     │
│       ┌────────────┐          │      │  │   ┌─────────────────┐  │     │
│       │  REST API  │          │      │  │   │ AniWatch Scraper │  │     │
│       │  /extract  │          │      │  │   │ ┌─────────────┐  │  │     │
│       │  /search   │          │      │  │   │ │ Episode ID  │  │  │     │
│       └─────┬──────┘          │      │  │   │ │ Servers     │  │  │     │
│             │                 │      │  │   │ │ Embed URL   │  │  │     │
└─────────────┼─────────────────┼──────┘  │   │ └─────────────┘  │  │     │
              │                 │         │   │         │         │  │     │
              ▼                 │         │   │         ▼         │  │     │
┌─────────────────────────────┐│         │   │ ┌─────────────────┐│  │     │
│    DEPLOYMENT OPTIONS       ││         │   │ │ MegaCloud       ││  │     │
│                            ││         │   │ │ Extractor       ││  │     │
│  ┌─────────────────────┐  ││         │   │ │ ┌─────────────┐││  │     │
│  │ Vercel Serverless   │  ││         │   │ │ │ JS          │││  │     │
│  │ 🟢 api.py + uvicorn│  ││         │   │ │ │ Deobfuscate │││  │     │
│  └─────────────────────┘  ││         │   │ │ └─────────────┘││  │     │
│                            ││         │   │ └─────────────────┘│  │     │
│  ┌─────────────────────┐  ││         │   └─────────────────────┘  │     │
│  │ Cloudflare Workers  │  ││         │            │              │     │
│  │ 🟡 worker.js       │  ││         │            ▼              │     │
│  └─────────────────────┘  ││         │   ┌─────────────────┐  │     │
│                            ││         │   │   M3U8 URL       │  │     │
│  ┌─────────────────────┐  ││         │   │   1080p! 🎉      │  │     │
│  │ Self-hosted VPS     │  ││         │   └─────────────────┘  │     │
│  │ 🟢 api.py + gunicorn│  ││         │                         │     │
│  └─────────────────────┘  ││         └─────────────────────────┘     │
└────────────────────────────┘│                                           │
                               └───────────────────────────────────────────┘
```

---

## 🔓 HOW THE HACK WORKS

### Step 1: Cloudflare Bypass (The Gatekeeper)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLOUDFLARE BYPASS                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
    │   NORMAL PYTHON │         │   CLOUDFLARE    │         │   curl_cffi     │
    │                  │         │                  │         │                  │
    │  requests.get() │         │  Security Check │         │  impersonate=    │
    │       │         │         │       │        │         │  "chrome120"     │
    │       ▼         │         │       ▼        │         │       │         │
    │  "Hi I'm Python"│         │ ┌────────────┐ │         │       ▼         │
    │                  │         │ │🚫 BLOCKED!│ │         │ "Hi I'm Chrome" │
    │  ❌ 403 Error   │         │ └────────────┘ │         │                  │
    │                  │         │                │         │  ✅ ALLOWED!    │
    └──────────────────┘         └──────────────────┘         └──────────────────┘

INSTALLATION:
    pip install curl_cffi

USAGE:
    from curl_cffi import requests
    resp = requests.get(url, impersonate="chrome120")
```

### Step 2: Finding the Hidden API

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NETWORK SNOOPING                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Chrome DevTools → Network Tab → Watch video load:

    ┌───────────────────────────────────────────────────────────────────┐
    │                                                                   │
    │  Name                    │ Status │ Type  │ Size   │ Time        │
    │  ────────────────────────┼────────┼───────┼────────┼────────     │
    │  ?id=ABC123             │ 200    │ xhr   │ 1.2 KB │ 45ms        │
    │                                                                   │
    │  ┌───────────────────────────────────────────────────────────────┐ │
    │  │ Headers │ Payload │ Preview │ Timing                        │ │
    │  ├───────────────────────────────────────────────────────────────┤ │
    │  │ Preview:                                                      │ │
    │  │ {                                                             │ │
    │  │   "sources": [{                                               │ │
    │  │     "file": "https://vod.netmagcdn.com/.../master.m3u8"      │ │
    │  │   }]                                                          │ │
    │  │ }                                                             │ │
    │  └───────────────────────────────────────────────────────────────┘ │
    │                                                                   │
    └───────────────────────────────────────────────────────────────────┘

FOUND: GET /embed-2/v3/e-1/getSources?id=VIDEO_ID&_k=CLIENT_KEY
```

### Step 3: JavaScript Deobfuscation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MEGACLOUD OBFUSCATED JAVASCRIPT                       │
└─────────────────────────────────────────────────────────────────────────────┘

WHAT IT LOOKS LIKE (Obfuscated):
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  // 1000+ lines of confusing code like this:                               │
│                                                                             │
│  var _0x5e6f=['xHR0cHM6Ly8','bWVnYWNsb3Vk','LnRscy8=',...]             │
│  _0x1234=function(_0x5678){return _0x9abc[_0xdef0](...)}                 │
│  var _0xh1i2={x:'MryTi1q',y:'obRhDNHw',z:'TuwVBE9'}                     │
│                                                                             │
│  // Computed values, XOR operations, array shuffling...                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

WHAT IT DOES (Deobfuscated by us):
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  1. Extract client key: x + y + z                                          │
│     → "MryTi1qobRhDNHwTuwVBE9Z0HTDSi4QlULMiRIswKXNTaY25"               │
│                                                                             │
│  2. Call API: /getSources?id=ID&_k=CLIENT_KEY                             │
│                                                                             │
│  3. Decrypt response:                                                     │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │  ENCRYPTED: "VGhpcyBpcyBlbmNyeXB0ZWQ..."                       │   │
│     │       │                                                        │   │
│     │       ▼  Base64 decode                                         │   │
│     │  "encrypted_data"                                               │   │
│     │       │                                                        │   │
│     │       ▼  XOR with LCG hash                                     │   │
│     │  "shuffled_data"                                                │   │
│     │       │                                                        │   │
│     │       ▼  Unshuffle array                                       │   │
│     │  "https://vod.netmagcdn.com/.../master.m3u8"                   │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 THE DECRYPTION ALGORITHM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LCG + XOR DECRYPTION                                 │
└─────────────────────────────────────────────────────────────────────────────┘

LCG (Linear Congruential Generator):
    next = (current * 1103515245 + 12345) & 0x7FFFFFFF

XOR Decryption:
    for each character:
        hash = LCG(hash)
        val1 = ord(char) - 32
        val2 = hash % 95
        decrypted_char = chr((val1 - val2) % 95 + 32)

Array Shuffle (Fisher-Yates Reverse):
    for i in range(len(array)-1, 0, -1):
        j = key_hash % (i + 1)
        array[i], array[j] = array[j], array[i]
```

---

## 🚀 DEPLOYMENT OPTIONS

### Option 1: Vercel Serverless

```bash
# Install dependencies
pip install curl_cffi requests fastapi uvicorn

# Create vercel.json (already created)
# Deploy!
vercel deploy

# Or run locally
python3 api.py
```

**API Endpoints:**
```
GET /api/extract?slug=anime-slug&episode=1
GET /api/search?query=naruto
```

### Option 2: Cloudflare Workers

```bash
# Install Wrangler
npm install -g wrangler

# Deploy
wrangler deploy
```

**API Endpoints:**
```
GET /?slug=anime-slug&episode=1
```

### Option 3: Self-hosted VPS

```bash
# Install
pip install curl_cffi requests fastapi uvicorn gunicorn

# Run
gunicorn api:app -b 0.0.0.0:8000
```

---

## 💾 FILES CREATED

| File | Purpose |
|------|---------|
| `api.py` | Main API server (Vercel/VPS) |
| `aniwatch_extractor.py` | Full CLI extractor |
| `megacloud_extractor.py` | JS deobfuscation module |
| `worker.js` | Cloudflare Workers version |
| `vercel.json` | Vercel config |
| `wrangler.toml` | Cloudflare config |

---

## ⭐ DIFFICULTY RATING

| Task | Difficulty | Why |
|------|------------|-----|
| Finding the API | ⭐ Easy | Network tab in DevTools |
| Cloudflare bypass | ⭐⭐⭐ Hard | TLS fingerprinting needed |
| JS Deobfuscation | ⭐⭐⭐⭐ Extreme | 1000+ lines of obfuscated JS |
| Key extraction | ⭐⭐⭐⭐ Extreme | Complex regex + algorithms |
| Decryption logic | ⭐⭐⭐⭐⭐ Insane | LCG, XOR, shuffle math |

**OVERALL: ⭐⭐⭐⭐ HARD (but doable!)**

---

## 💡 THE KEY INSIGHT

**If a BROWSER can do it, WE CAN DO IT TOO!**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE SECRET                                        │
└─────────────────────────────────────────────────────────────────────────────┘

    Browser:        "I can read this JavaScript and play the video"
                          │
                          ▼
    We:             "If the browser can do it, let's study HOW it works!"
                          │
                          ▼
    DevTools:       "Look at the network requests..."
                          │
                          ▼
    Found API:      "/getSources?id=ID&_k=KEY"
                          │
                          ▼
    Replicate:      "Write Python that does what the browser does"
                          │
                          ▼
    🎉 M3U8 URL:    "https://vod.netmagcdn.com/.../master.m3u8"
```

---

## 📦 INSTALLATION

```bash
# Required packages
pip install curl_cffi requests

# Optional (for full API)
pip install fastapi uvicorn

# Test the extractor
python3 aniwatch_extractor.py code-geass-lelouch-of-the-rebellion-r2-17 1
```

---

## 🎯 USAGE EXAMPLES

```bash
# CLI extraction
python3 aniwatch_extractor.py code-geass-lelouch-of-the-rebellion-r2-17 1

# API server
python3 api.py extract code-geass-lelouch-of-the-rebellion-r2-17 1
python3 api.py search naruto

# Cloudflare Workers
curl "https://aniwatch-api.workers.dev/?slug=code-geass-lelouch-of-the-rebellion-r2-17&episode=1"
```

---

## 🔗 REFERENCE

Based on yt-dlp hianime plugin's megacloud module
- GitHub: https://github.com/pratikpatel8982/yt-dlp-hianime
- Stars: 37+
- They already reverse-engineered MegaCloud!

---

**YOU ARE NOW A CERTIFIED MEGACLOUD HACKER!** 💪🔥
