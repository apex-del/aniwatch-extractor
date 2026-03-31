#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ANIWATCH/MEGACLOUD API - V6.6.1                      ║
║                         REST API FOR EXTRACTION                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

INSTALLATION:
    pip install curl_cffi requests fastapi uvicorn

USAGE (CLI):
    python3 api.py extract <slug> <episode>
    python3 api.py search <query>
    
    Examples:
        python3 api.py extract monster-37 1
        python3 api.py search naruto

USAGE (API SERVER):
    uvicorn api:app --host 0.0.0.0 --port 8000
    
    Then visit:
        http://localhost:8000/api/extract?slug=monster-37&episode=1
        http://localhost:8000/api/search?query=death%20note

API ENDPOINTS:
    GET /api/extract?slug=<anime-slug>&episode=<number>
        Returns JSON with M3U8 URL, subtitles, intro/outro times
        
    GET /api/search?query=<search-term>
        Returns list of matching anime

DEPLOYMENT:
    - Vercel: vercel deploy
    - Cloudflare Workers: wrangler deploy
    - VPS: gunicorn api:app -b 0.0.0.0:8000

EXAMPLE RESPONSE:
    {
        "success": true,
        "m3u8_url": "https://vod.netmagcdn.com:2228/hls/.../master.m3u8",
        "embed_url": "https://megacloud.blog/embed-2/v3/e-1/...",
        "intro": {"start": 148, "end": 244},
        "outro": {"start": 1336, "end": 1428},
        "tracks": [
            {"label": "English", "file": "...vtt"},
            {"label": "Arabic", "file": "...vtt"}
        ]
    }

╔══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  Requires curl_cffi for Cloudflare bypass.                       ║
║  💡  Cloudflare may block server IPs - use residential proxy if needed.║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import re
import time
from typing import Optional, Dict, List, Any

# Try curl_cffi first, fallback to requests
CURL_CFFI_AVAILABLE = False
try:
    from curl_cffi import requests as cf_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    import requests as cf_requests

# MegaCloud extractor
try:
    from megacloud_extractor import Megacloud, make_request
except ImportError:
    Megacloud = None
    make_request = None


class AniWatchAPI:
    """AniWatch/MegaCloud API for anime streaming extraction"""
    
    BASE_URL = "https://aniwatchtv.to"
    MEGACLOUD_BASE = "https://megacloud.blog"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    MEGACLOUD_HEADERS = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
        "origin": MEGACLOUD_BASE,
        "referer": MEGACLOUD_BASE + "/",
    }

    def __init__(self):
        self.session = None
        if CURL_CFFI_AVAILABLE:
            self._request = self._cf_request
        else:
            self._request = self._requests_fallback

    def _cf_request(self, url: str, params: dict = None, retries: int = 3) -> Optional[dict]:
        """Request with curl_cffi"""
        for attempt in range(retries):
            try:
                resp = cf_requests.get(
                    url,
                    headers=self.HEADERS,
                    params=params,
                    impersonate="chrome120",
                    timeout=30
                )
                return resp
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return None

    def _requests_fallback(self, url: str, params: dict = None, retries: int = 3) -> Optional[dict]:
        """Fallback to requests (may be blocked by Cloudflare)"""
        for attempt in range(retries):
            try:
                resp = cf_requests.get(url, headers=self.HEADERS, params=params, timeout=30)
                return resp
            except:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return None

    def search(self, query: str) -> List[Dict]:
        """Search for anime"""
        url = f"{self.BASE_URL}/ajax/search"
        resp = self._request(url, params={"keyword": query})
        if not resp or resp.status_code != 200:
            return []
        
        try:
            data = resp.json()
            html = data.get("result", {}).get("html", "")
            
            titles = re.findall(r'<h6[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</h6>', html)
            links = re.findall(r'href="(/watch/[^"]+)"', html)
            
            results = []
            for i, title in enumerate(titles):
                slug = links[i] if i < len(links) else ""
                slug_clean = slug.replace("/watch/", "").split("?")[0]
                results.append({
                    "title": title.strip(),
                    "slug": slug_clean,
                    "url": f"{self.BASE_URL}{slug}",
                })
            return results
        except:
            return []

    def get_episode_id(self, slug: str, episode: int = 1) -> Optional[str]:
        """Get episode ID from slug"""
        anime_id_match = re.search(r'-(\d+)$', slug)
        if not anime_id_match:
            return None
        
        anime_id = anime_id_match.group(1)
        url = f"{self.BASE_URL}/ajax/v2/episode/list/{anime_id}"
        resp = self._request(url)
        
        if not resp or resp.status_code != 200:
            return None
        
        try:
            data = resp.json()
            html = data.get("html", "")
            ep_matches = re.findall(r'\?ep=(\d+)', html)
            
            if ep_matches:
                return ep_matches[episode - 1] if episode <= len(ep_matches) else ep_matches[0]
            return None
        except:
            return None

    def get_servers(self, episode_id: str) -> List[Dict]:
        """Get available servers"""
        url = f"{self.BASE_URL}/ajax/v2/episode/servers"
        resp = self._request(url, params={"episodeId": episode_id})
        if not resp or resp.status_code != 200:
            return []
        
        try:
            data = resp.json()
            html = data.get("html", "")
            
            servers = []
            items = re.findall(
                r'<div[^>]*data-type="(sub|dub)"[^>]*data-id="(\d+)"[^>]*data-server-id="\d+"[^>]*>.*?<a[^>]*class="btn"[^>]*>([^<]+)</a>',
                html,
                re.DOTALL
            )
            
            for server_type, server_id, server_name in items:
                servers.append({
                    "id": server_id,
                    "name": server_name.strip(),
                    "type": server_type
                })
            return servers
        except:
            return []

    def get_source(self, server_id: str) -> Optional[str]:
        """Get embed URL from server"""
        url = f"{self.BASE_URL}/ajax/v2/episode/sources"
        resp = self._request(url, params={"id": server_id})
        if not resp or resp.status_code != 200:
            return None
        
        try:
            return resp.json().get("link")
        except:
            return None

    def extract_megacloud(self, embed_url: str) -> Optional[Dict]:
        """Extract M3U8 from megacloud embed"""
        if not Megacloud or not make_request:
            return None
        
        try:
            source_id_match = re.search(r'embed-2/v3/e-1/([a-zA-Z0-9]+)', embed_url)
            if not source_id_match:
                return None
            
            source_id = source_id_match.group(1)
            
            resp = make_request(embed_url, self.MEGACLOUD_HEADERS)
            if not resp:
                return None
            
            html = resp.text
            
            client_key_patterns = [
                r'([a-zA-Z0-9]{48})',
                r'x:\s*"([a-zA-Z0-9]{16})"',
                r'y:\s*"([a-zA-Z0-9]{16})"',
                r'z:\s*"([a-zA-Z0-9]{16})"',
            ]
            
            client_key = ""
            for pattern in client_key_patterns:
                match = re.search(pattern, html)
                if match:
                    client_key += match.group(1)
            
            if not client_key or len(client_key) < 16:
                client_key = "anonymous"
            
            get_src_url = f"{self.MEGACLOUD_BASE}/embed-2/v3/e-1/getSources"
            resp = make_request(get_src_url, self.MEGACLOUD_HEADERS, {"id": source_id, "_k": client_key})
            
            if not resp:
                return None
            
            return resp.json()
        except:
            return None

    def extract(self, slug: str, episode: int = 1) -> Dict:
        """Main extraction method - returns JSON response"""
        episode_id = self.get_episode_id(slug, episode)
        if not episode_id:
            return {"success": False, "error": "Episode not found"}
        
        servers = self.get_servers(episode_id)
        if not servers:
            return {"success": False, "error": "No servers found"}
        
        # Try MegaCloud first
        embed_url = None
        for server in servers:
            if 'mega' in server["name"].lower():
                source = self.get_source(server["id"])
                if source:
                    embed_url = source
                    break
        
        if not embed_url:
            for server in servers:
                if server["type"] == "sub":
                    source = self.get_source(server["id"])
                    if source:
                        embed_url = source
                        break
        
        if not embed_url:
            return {"success": False, "error": "No embed URL found"}
        
        result = self.extract_megacloud(embed_url)
        if not result or not result.get("sources"):
            return {"success": False, "error": "Failed to extract M3U8"}
        
        sources = result.get("sources", [])
        m3u8_url = sources[0].get("file") if sources else None
        
        if not m3u8_url:
            return {"success": False, "error": "No M3U8 URL"}
        
        return {
            "success": True,
            "slug": slug,
            "episode": episode,
            "m3u8_url": m3u8_url,
            "embed_url": embed_url,
            "episode_id": episode_id,
            "intro": result.get("intro", {}),
            "outro": result.get("outro", {}),
            "tracks": result.get("tracks", []),
        }


# ===================== VERCEL/CLOUDFLARE HANDLER =====================

def handler(event, context=None):
    """Vercel/Cloudflare handler"""
    query = event.get("queryStringParameters") or {}
    
    slug = query.get("slug")
    episode = int(query.get("episode", 1))
    search_query = query.get("search")
    
    api = AniWatchAPI()
    
    # Search endpoint
    if search_query:
        results = api.search(search_query)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"success": True, "results": results})
        }
    
    # Extract endpoint
    if slug:
        result = api.extract(slug, episode)
        return {
            "statusCode": 200 if result.get("success") else 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
    
    # No parameters
    return {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "success": False,
            "error": "Missing parameters. Use ?slug=...&episode=1 or ?search=..."
        })
    }


# ===================== LOCAL TESTING =====================

if __name__ == "__main__":
    import sys
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║          AniWatch/MegaCloud API - V6.6.1                       ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 api.py extract <slug> <episode>")
        print("  python3 api.py search <query>")
        print()
        print("Examples:")
        print("  python3 api.py extract code-geass-lelouch-of-the-rebellion-r2-17 1")
        print("  python3 api.py search naruto")
        sys.exit(1)
    
    command = sys.argv[1]
    api = AniWatchAPI()
    
    if command == "extract":
        slug = sys.argv[2] if len(sys.argv) > 2 else ""
        episode = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        
        if not slug:
            print("Error: slug required")
            sys.exit(1)
        
        print(f"Extracting: {slug} Episode {episode}")
        result = api.extract(slug, episode)
        print(json.dumps(result, indent=2))
    
    elif command == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        
        if not query:
            print("Error: search query required")
            sys.exit(1)
        
        print(f"Searching: {query}")
        results = api.search(query)
        print(json.dumps(results, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
