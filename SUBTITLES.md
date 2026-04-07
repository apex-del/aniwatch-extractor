# 🎬 SUBTITLES/CC EXTRACTED FROM MEGACLOUD

## 🎉 YES! ALL SUBTITLES ARE EXTRACTED!

The API returns **ALL** available subtitles for each episode!

---

## 📝 EXAMPLE: Code Geass R2 Episode 1

The extractor returns ALL 8 subtitle languages:

```json
{
  "success": true,
  "m3u8_url": "https://vod.netmagcdn.com:2228/hls/.../master.m3u8",
  "tracks": [
    {
      "file": "https://mgstatics.xyz/subtitle/.../ara-3.vtt",
      "label": "Arabic",
      "kind": "captions"
    },
    {
      "file": "https://mgstatics.xyz/subtitle/.../eng-2.vtt",
      "label": "English",
      "kind": "captions",
      "default": true
    },
    {
      "file": "https://mgstatics.xyz/subtitle/.../fre-4.vtt",
      "label": "French",
      "kind": "captions"
    },
    {
      "file": "https://mgstatics.xyz/subtitle/.../ger-5.vtt",
      "label": "German",
      "kind": "captions"
    },
    {
      "file": "https://mgstatics.xyz/subtitle/.../ita-6.vtt",
      "label": "Italian",
      "kind": "captions"
    },
    {
      "file": "https://mgstatics.xyz/subtitle/.../por-7.vtt",
      "label": "Portuguese",
      "kind": "captions"
    },
    {
      "file": "https://mgstatics.xyz/subtitle/.../spa-9.vtt",
      "label": "Spanish",
      "kind": "captions"
    },
    {
      "file": "https://mgstatics.xyz/subtitle/.../spa-8.vtt",
      "label": "Spanish - Spanish(ES)",
      "kind": "captions"
    },
    {
      "file": "https://mgstatics.xyz/thumbnails/.../thumbnails.vtt",
      "kind": "thumbnails"
    }
  ]
}
```

---

## 🌐 Available Subtitle Languages

Based on extraction, these languages are available:

| # | Language | Code | Status |
|---|----------|------|--------|
| 1 | English | eng | DEFAULT |
| 2 | Arabic | ara | Available |
| 3 | French | fre | Available |
| 4 | German | ger | Available |
| 5 | Italian | ita | Available |
| 6 | Portuguese | por | Available |
| 7 | Spanish | spa | Available |
| 8 | Spanish (ES) | spa | Available |

---

## 📂 Subtitle Source

Subtitles are stored on: `mgstatics.xyz`

Format: `https://mgstatics.xyz/subtitle/{HASH}/{LABEL}.vtt`

Example:
```
https://mgstatics.xyz/subtitle/81e4c4862e5fe518758922ef1348cf2e/eng-2.vtt
```

---

## 🔧 HOW TO USE SUBTITLES

### With yt-dlp (Download with subtitles):
```bash
# Download all subtitles
yt-dlp --write-subs --all-subs \
       --headers "Referer: https://megacloud.tv/" \
       "M3U8_URL"

# Download specific language
yt-dlp --write-subs --sub-lang en \
       --headers "Referer: https://megacloud.tv/" \
       "M3U8_URL"
```

### With FFmpeg (Burn subtitles into video):
```bash
# Burn English subtitles
ffmpeg -i video.m3u8 -vf "subtitles=eng.vtt" output.mp4

# Burn with specific language
ffmpeg -i video.m3u8 -vf "subtitles=ara-3.vtt" output.mp4
```

### With Video Players:
| Player | Method |
|--------|--------|
| VLC | Media → Open File → Subtitle track |
| MPV | `--sub-file=subs.vtt` |
| MX Player | Select subtitle track |
| Kodi | Subtitles → Open file |

---

## 📺 VTT File Format

Subtitles are in WebVTT format:

```
WEBVTT

00:00:01.000 --> 00:00:04.000
[The episode begins]

00:00:05.000 --> 00:00:08.000
Kenji is walking home from school...

00:00:10.000 --> 00:00:14.000
<b>Bold text</b>
<i>Italic text</i>
```

---

## ⚠️ IMPORTANT NOTES

1. **URLs expire!** Subtitle URLs expire with the M3U8
2. **Download immediately** after extraction
3. **Thumbnails** track is for video preview scrubber

---

**Subtitles extracted from: MegaCloud (megacloud.tv)**
