#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 ANIWATCH/MEGACLOUD EXTRACTOR - V6.6.1                    ║
║                       HACK THE STREAMING ENGINE!                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

INSTALLATION:
    pip install curl_cffi requests

USAGE (CLI):
    python3 aniwatch_extractor.py <anime-slug> <episode>
    
    Examples:
        python3 aniwatch_extractor.py death-note-60 1
        python3 aniwatch_extractor.py monster-37 1
        python3 aniwatch_extractor.py code-geass-lelouch-of-the-rebellion-r2-17 1
        python3 aniwatch_extractor.py naruto-677 220

USAGE (Python):
    from aniwatch_extractor import AniwatchExtractor
    
    extractor = AniwatchExtractor()
    result = extractor.extract("monster-37", 1)
    
    if result:
        print(f"M3U8: {result['m3u8_url']}")
        print(f"Intro: {result['intro']}")
        print(f"Outro: {result['outro']}")

HOW IT WORKS:
    1. Bypass Cloudflare with curl_cffi (TLS fingerprinting)
    2. Get episode ID from aniwatchtv.to
    3. Get available servers (MegaCloud, VidSrc, etc.)
    4. Get MegaCloud embed URL
    5. Deobfuscate JavaScript to extract M3U8 URL
    
FIND SLUG:
    - Go to aniwatchtv.to
    - Search for anime
    - Copy slug from URL: aniwatchtv.to/watch/<THIS-PART>?ep=123
    - Example: monster-37

AUTHOR: V6.6.1 Project
BASED ON: yt-dlp hianime plugin megacloud module

╔══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  URLs expire quickly! Use fresh extraction each time.              ║
║  💡 Tip: Download immediately with yt-dlp after extraction.            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import re
import subprocess
import sys
from typing import Optional, Dict, List, Any

CURL_CFFI_AVAILABLE = False
try:
    from curl_cffi import requests as cf_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    cf_requests = None


class AniwatchExtractor:
    """Extract M3U8 from AniWatch/HiAnime using Megacloud"""

    BASE_URLS = [
        "https://aniwatchtv.to",
        "https://hianimez.to",
        "https://hianime.to",
        "https://hianime.vc",
    ]

    MEGACLOUD_BASE = "https://megacloud.blog"
    MEGACLOUD_HEADERS = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
        "origin": MEGACLOUD_BASE,
        "referer": MEGACLOUD_BASE + "/",
    }

    def __init__(self, base_url: str = None, impersonate: str = "chrome120"):
        self.base_url = base_url or self.BASE_URLS[0]
        self.impersonate = impersonate
        self.session_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.base_url + "/",
        }

    def _request(self, url: str, params: dict = None, retries: int = 3) -> Optional[cf_requests.Response]:
        """Make request with curl_cffi Cloudflare bypass and retry"""
        if not CURL_CFFI_AVAILABLE:
            print("curl_cffi not available, falling back to curl")
            return None
        
        for attempt in range(retries):
            try:
                resp = cf_requests.get(
                    url,
                    headers=self.session_headers,
                    params=params,
                    impersonate=self.impersonate,
                    timeout=30,
                    verify=False
                )
                return resp
            except Exception as e:
                if attempt < retries - 1:
                    import time
                    time.sleep(2)
                    continue
                print(f"Request error: {e}")
                return None

    def search(self, query: str) -> List[Dict]:
        """Search for anime"""
        url = f"{self.base_url}/ajax/search"
        resp = self._request(url, params={"keyword": query})
        if not resp or resp.status_code != 200:
            return []
        
        try:
            data = resp.json()
            html = data.get("result", {}).get("html", "")
            
            titles = re.findall(r'<h6[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</h6>', html)
            links = re.findall(r'href="(/watch/[^"]+)"', html)
            posters = re.findall(r'src="([^"]+)"[^>]*class="[^"]*poster', html)
            
            results = []
            for i, title in enumerate(titles):
                slug = links[i] if i < len(links) else ""
                results.append({
                    "title": title.strip(),
                    "slug": slug,
                    "url": f"{self.base_url}{slug}",
                    "poster": posters[i] if i < len(posters) else ""
                })
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_episode_id(self, anime_slug: str, episode: int = 1) -> Optional[str]:
        """Get episode ID from anime page"""
        try:
            anime_id_match = re.search(r'-(\d+)$', anime_slug)
            if not anime_id_match:
                return None
            
            anime_id = anime_id_match.group(1)
            
            list_url = f"{self.base_url}/ajax/v2/episode/list/{anime_id}"
            resp = self._request(list_url)
            
            if not resp or resp.status_code != 200:
                return None
            
            data = resp.json()
            html = data.get("html", "")
            
            ep_matches = re.findall(r'\?ep=(\d+)', html)
            
            if ep_matches:
                return ep_matches[episode - 1] if episode <= len(ep_matches) else ep_matches[0]
            
            return None
        except Exception as e:
            print(f"Get episode ID error: {e}")
            return None

    def get_servers(self, episode_id: str) -> List[Dict]:
        """Get available servers for episode"""
        url = f"{self.base_url}/ajax/v2/episode/servers"
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
        except Exception as e:
            print(f"Get servers error: {e}")
            return []

    def get_source(self, server_id: str) -> Optional[str]:
        """Get megacloud embed URL from server"""
        url = f"{self.base_url}/ajax/v2/episode/sources"
        resp = self._request(url, params={"id": server_id})
        if not resp or resp.status_code != 200:
            return None
        
        try:
            data = resp.json()
            return data.get("link")
        except:
            return None

    def extract_megacloud(self, embed_url: str) -> Optional[Dict]:
        """Extract M3U8 from megacloud embed URL"""
        from megacloud_extractor import Megacloud, make_request
        
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
        except Exception as e:
            print(f"Megacloud extraction error: {e}")
            return None

    def extract(self, anime_slug: str, episode: int = 1, type: str = "sub") -> Optional[Dict]:
        """Main extraction method
        
        Args:
            anime_slug: Anime slug (e.g., 'monster-37')
            episode: Episode number (1, 2, 3, etc.)
            type: Stream type - 'sub' for subtitles, 'dub' for dubbed audio
            
        Returns:
            Dict with m3u8_url, tracks, success, etc.
        """
        print(f"\n{'='*60}")
        print(f"AniWatch/MegaCloud Extractor")
        print(f"{'='*60}")
        print(f"Anime: {anime_slug}, Episode: {episode}")
        print(f"Stream Type: {type.upper()}")
        print(f"Base URL: {self.base_url}")
        
        print("\n[1/4] Getting episode ID...")
        episode_id = self.get_episode_id(anime_slug, episode)
        if not episode_id:
            print("❌ Failed to get episode ID")
            return None
        print(f"✅ Episode ID: {episode_id}")
        
        print("\n[2/4] Getting servers...")
        servers = self.get_servers(episode_id)
        if not servers:
            print("❌ No servers found")
            return None
        print(f"✅ Found {len(servers)} servers")
        
        # Filter servers by type (sub/dub)
        type_filtered = [s for s in servers if s.get("type") == type]
        if type_filtered:
            print(f"✅ Found {len(type_filtered)} {type.upper()} servers")
            servers = type_filtered
        
        print("\n[3/4] Getting MegaCloud embed URL...")
        embed_url = None
        source = None
        used_server = None
        
        # Priority: MegaCloud > Mega > Cloud > then others (within filtered type)
        for server in servers:
            name_lower = server["name"].lower()
            if "mega" in name_lower:
                source = self.get_source(server["id"])
                if source:
                    embed_url = source
                    used_server = server
                    print(f"✅ Found {server['name']} ({type.upper()}): {source[:60]}...")
                    break
        
        if not embed_url:
            for server in servers:
                name_lower = server["name"].lower()
                if "cloud" in name_lower and "t-" not in name_lower:
                    source = self.get_source(server["id"])
                    if source:
                        embed_url = source
                        used_server = server
                        print(f"✅ Found {server['name']} ({type.upper()}): {source[:60]}...")
                        break
        
        if not embed_url:
            # Fallback: try any server of the requested type
            for server in servers:
                if server["type"] == type:
                    source = self.get_source(server["id"])
                    if source:
                        embed_url = source
                        used_server = server
                        print(f"✅ Found {server['name']} ({type.upper()}): {source[:60]}...")
                        break
        
        if not embed_url:
            print(f"❌ No {type.upper()} megacloud embed URL found")
            # Try opposite type as last resort
            if type == "sub":
                print("⚠️  Trying DUB servers as fallback...")
                fallback = [s for s in servers if s.get("type") == "dub"]
            else:
                print("⚠️  Trying SUB servers as fallback...")
                fallback = [s for s in servers if s.get("type") == "sub"]
            
            for server in fallback:
                source = self.get_source(server["id"])
                if source:
                    embed_url = source
                    used_server = server
                    print(f"✅ Found {server['name']} (fallback): {source[:60]}...")
                    break
        
        if not embed_url:
            print("❌ No embed URL found")
            return None
        
        print("\n[4/4] Extracting M3U8...")
        result = self.extract_megacloud(embed_url)
        if not result:
            print("❌ Failed to extract M3U8")
            return None
        
        sources = result.get("sources", [])
        m3u8_url = sources[0].get("file") if sources else None
        
        if not m3u8_url:
            print("❌ No M3U8 URL in result")
            return None
        
        print(f"\n✅ SUCCESS!")
        print(f"M3U8 URL: {m3u8_url[:80]}...")
        
        return {
            "success": True,
            "m3u8_url": m3u8_url,
            "sources": sources,
            "tracks": result.get("tracks", []),
            "intro": result.get("intro", {}),
            "outro": result.get("outro", {}),
            "embed_url": embed_url,
            "episode_id": episode_id,
            "episode": episode,
            "anime_slug": anime_slug,
            "type": type,
            "server_type": used_server.get("type") if used_server else None,
            "servers": servers
        }


def main():
    if len(sys.argv) < 2:
        print("""
╔═══════════════════════════════════════════════════════════════╗
║     AniWatch/MegaCloud M3U8 Extractor - V6.6.1          ║
╠═══════════════════════════════════════════════════════════════╣
║  Usage: python aniwatch_extractor.py <slug> [episode] [type]
║                                                               ║
║  Examples:                                                   ║
║    python aniwatch_extractor.py naruto-677 1                 ║
║    python aniwatch_extractor.py one-piece-100 1              ║
║    python aniwatch_extractor.py one-piece-100 1 sub           ║
║    python aniwatch_extractor.py one-piece-100 1 dub           ║
╚═══════════════════════════════════════════════════════════════╝
        """)
        sys.exit(1)
    
    anime_slug = sys.argv[1]
    episode = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    type_param = sys.argv[3].lower() if len(sys.argv) > 3 else "sub"
    
    # Validate type
    if type_param not in ["sub", "dub"]:
        print("❌ Type must be 'sub' or 'dub'")
        sys.exit(1)
    
    extractor = AniwatchExtractor()
    result = extractor.extract(anime_slug, episode, type_param)
    
    if result:
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    ✅ EXTRACTION SUCCESS                     ║
╠═══════════════════════════════════════════════════════════════╣
║  M3U8 URL: {result['m3u8_url'][:55]}
║  Type: {result.get('type', 'N/A').upper()}
║  Intro: {result.get('intro', {}).get('start', 'N/A')}s - {result.get('intro', {}).get('end', 'N/A')}s
║  Outro: {result.get('outro', {}).get('start', 'N/A')}s - {result.get('outro', {}).get('end', 'N/A')}s
╚═══════════════════════════════════════════════════════════════╝
        """)
    else:
        print("\n❌ Extraction failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
