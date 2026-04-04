"""
AniWatch/MegaCloud Extractor API for Vercel (Flask)
"""

import json
import re
import urllib.request
from flask import Flask, request, jsonify

app = Flask(__name__)

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
    except:
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
    """Get available servers for episode with type (sub/dub) info"""
    html = get(f"{BASE_URL}/ajax/v2/episode/servers", HEADERS, {"episodeId": episode_id})
    if not html:
        return []
    try:
        data = json.loads(html)
        html = data.get("html", "")
        # Extract type (sub/dub), server id, and server name
        items = re.findall(
            r'<div[^>]*data-type="(sub|dub)"[^>]*data-id="(\d+)"[^>]*data-server-id="\d+"[^>]*>.*?<a[^>]*class="btn"[^>]*>([^<]+)</a>',
            html, re.DOTALL
        )
        servers = []
        for server_type, server_id, server_name in items:
            servers.append({
                "id": server_id,
                "name": server_name.strip(),
                "type": server_type
            })
        return servers
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


def extract(slug, episode=1, type="sub"):
    """Extract M3U8 with type (sub/dub) support
    
    Args:
        slug: Anime slug (e.g., 'monster-37')
        episode: Episode number
        type: 'sub' or 'dub'
    """
    episode_id = get_episode_id(slug, episode)
    if not episode_id:
        return {"success": False, "error": "Episode not found"}
    
    servers = get_servers(episode_id)
    if not servers:
        return {"success": False, "error": "No servers found"}
    
    # Filter servers by type
    type_filtered = [s for s in servers if s.get("type") == type]
    if type_filtered:
        servers_to_use = type_filtered
    else:
        servers_to_use = servers  # Fallback to all if no filtered servers
    
    embed_url = None
    used_server = None
    
    # Priority: MegaCloud > Mega > Cloud
    for server in servers_to_use:
        if 'mega' in server["name"].lower():
            source = get_source(server["id"])
            if source:
                embed_url = source
                used_server = server
                break
    
    if not embed_url:
        for server in servers_to_use:
            if 'cloud' in server["name"].lower():
                source = get_source(server["id"])
                if source:
                    embed_url = source
                    used_server = server
                    break
    
    if not embed_url:
        # Last resort: any server of requested type
        for server in servers_to_use:
            if server.get("type") == type:
                source = get_source(server["id"])
                if source:
                    embed_url = source
                    used_server = server
                    break
    
    if not embed_url:
        return {"success": False, "error": f"No {type} embed URL found"}
    
    m3u8_url, tracks = extract_megacloud(embed_url)
    
    if not m3u8_url:
        return {"success": False, "error": "Failed to extract M3U8"}
    
    return {
        "success": True,
        "slug": slug,
        "episode": episode,
        "type": type,
        "server_type": used_server.get("type") if used_server else None,
        "m3u8_url": m3u8_url,
        "embed_url": embed_url,
        "episode_id": episode_id,
        "tracks": tracks,
    }


@app.route('/')
def home():
    return jsonify({
        "name": "AniWatch/MegaCloud Extractor API",
        "usage": "/api/extract?slug=anime-slug&episode=1&type=sub",
        "examples": [
            "/api/extract?slug=monster-37&episode=1&type=sub",
            "/api/extract?slug=monster-37&episode=1&type=dub"
        ]
    })


@app.route('/api/extract')
def api_extract():
    slug = request.args.get('slug', '')
    episode = int(request.args.get('episode', 1))
    type_param = request.args.get('type', 'sub').lower()
    
    # Validate type parameter
    if type_param not in ["sub", "dub"]:
        return jsonify({"success": False, "error": "Type must be 'sub' or 'dub'"}), 400
    
    if not slug:
        return jsonify({"success": False, "error": "Missing slug parameter"}), 400
    
    result = extract(slug, episode, type_param)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
