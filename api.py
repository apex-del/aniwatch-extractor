"""
AniWatch/MegaCloud Extractor API for Vercel
"""

import json
import re
import urllib.request
import urllib.error

BASE_URL = "https://aniwatchtv.to"
MEGACLOUD_BASE = "https://megacloud.blog"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

MEGACLOUD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Origin": MEGACLOUD_BASE,
    "Referer": MEGACLOUD_BASE + "/",
}


def get(url, headers=None, params=None):
    if params:
        url += '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode()
    except Exception as e:
        return None


def get_episode_id(slug, episode=1):
    match = re.search(r'-(\d+)$', slug)
    if not match:
        return None
    anime_id = match.group(1)
    html = get(f"{BASE_URL}/ajax/v2/episode/list/{anime_id}", HEADERS)
    if not html:
        return None
    matches = re.findall(r'\?ep=(\d+)', html)
    if matches:
        return matches[episode - 1] if episode <= len(matches) else matches[0]
    return None


def get_servers(episode_id):
    html = get(f"{BASE_URL}/ajax/v2/episode/servers", HEADERS, {"episodeId": episode_id})
    if not html:
        return []
    try:
        data = json.loads(html)
        html = data.get("html", "")
        servers = re.findall(r'data-id="(\d+)"[^>]*data-server-id="\d+"[^>]*>.*?<a[^>]*class="btn"[^>]*>([^<]+)</a>', html, re.DOTALL)
        return [{"id": s[0], "name": s[1].strip()} for s in servers]
    except:
        return []


def get_source(server_id):
    html = get(f"{BASE_URL}/ajax/v2/episode/sources", HEADERS, {"id": server_id})
    if not html:
        return None
    try:
        data = json.loads(html)
        return data.get("link")
    except:
        return None


def extract_megacloud(embed_url):
    html = get(embed_url, MEGACLOUD_HEADERS)
    if not html:
        return None, []
    
    source_match = re.search(r'embed-2/v3/e-1/([a-zA-Z0-9]+)', embed_url)
    if not source_match:
        return None, []
    source_id = source_match.group(1)
    
    key_match = re.search(r'([a-zA-Z0-9]{48})', html)
    client_key = key_match.group(1) if key_match else "anonymous"
    
    api_url = f"{MEGACLOUD_BASE}/embed-2/v3/e-1/getSources?id={source_id}&_k={client_key}"
    data_str = get(api_url, MEGACLOUD_HEADERS)
    
    if not data_str:
        return None, []
    
    try:
        data = json.loads(data_str)
        sources = data.get("sources", [])
        if sources:
            m3u8 = sources[0].get("file") if isinstance(sources[0], dict) else sources[0]
            tracks = data.get("tracks", [])
            return m3u8, tracks
    except:
        pass
    return None, []


def extract(slug, episode=1):
    episode_id = get_episode_id(slug, episode)
    if not episode_id:
        return {"success": False, "error": "Episode not found"}
    
    servers = get_servers(episode_id)
    if not servers:
        return {"success": False, "error": "No servers found"}
    
    embed_url = None
    for server in servers:
        if 'mega' in server["name"].lower():
            source = get_source(server["id"])
            if source:
                embed_url = source
                break
    
    if not embed_url:
        for server in servers:
            source = get_source(server["id"])
            if source:
                embed_url = source
                break
    
    if not embed_url:
        return {"success": False, "error": "No embed URL found"}
    
    m3u8_url, tracks = extract_megacloud(embed_url)
    
    if not m3u8_url:
        return {"success": False, "error": "Failed to extract M3U8"}
    
    return {
        "success": True,
        "slug": slug,
        "episode": episode,
        "m3u8_url": m3u8_url,
        "embed_url": embed_url,
        "episode_id": episode_id,
        "tracks": tracks,
    }


def handler(req, res):
    """Vercel handler"""
    query = {}
    qs = req.query if hasattr(req, 'query') else ''
    for pair in (qs or '').split('&'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            query[k] = v
    
    slug = query.get('slug', '')
    episode = int(query.get('episode', 1))
    
    if not slug:
        res.status = 400
        res.header('Content-Type', 'application/json')
        res.send(json.dumps({"success": False, "error": "Missing slug parameter. Use ?slug=anime-slug&episode=1"}))
        return
    
    result = extract(slug, episode)
    res.status = 200 if result.get("success") else 404
    res.header('Content-Type', 'application/json')
    res.send(json.dumps(result))
