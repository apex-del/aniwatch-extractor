/**
 * Cloudflare Workers version of AniWatch/MegaCloud API
 * Deploy to Cloudflare Workers for global CDN
 * 
 * Wrangler deploy: wrangler deploy
 */

// MegaCloud extraction logic (simplified for Workers)
const MEGACLOUD_BASE = "https://megacloud.tv";
const MEGACLOUD_HEADERS = {
  "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
  "origin": MEGACLOUD_BASE,
  "referer": MEGACLOUD_BASE + "/",
};

async function fetchWithRetry(url, options = {}, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const resp = await fetch(url, options);
      return resp;
    } catch (e) {
      if (i < retries - 1) await new Promise(r => setTimeout(r, 1000));
    }
  }
  return null;
}

async function getEpisodeId(animeId, episode) {
  const url = `https://aniwatchtv.to/ajax/v2/episode/list/${animeId}`;
  const resp = await fetchWithRetry(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
    }
  });
  
  if (!resp || !resp.ok) return null;
  
  const html = await resp.text();
  const matches = [...html.matchAll(/\?ep=(\d+)/g)];
  
  if (matches.length > 0) {
    const epIndex = episode - 1;
    return matches[epIndex < matches.length ? epIndex : 0][1];
  }
  return null;
}

async function getServers(episodeId) {
  const url = `https://aniwatchtv.to/ajax/v2/episode/servers?episodeId=${episodeId}`;
  const resp = await fetchWithRetry(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
    }
  });
  
  if (!resp || !resp.ok) return [];
  
  const data = await resp.json();
  const html = data.html || "";
  
  const servers = [];
  const regex = /data-id="(\d+)"[^>]*data-server-id="\d+"[^>]*>.*?<a[^>]*class="btn"[^>]*>([^<]+)</g;
  let match;
  
  while ((match = regex.exec(html)) !== null) {
    servers.push({ id: match[1], name: match[2].trim() });
  }
  
  return servers;
}

async function getSource(serverId) {
  const url = `https://aniwatchtv.to/ajax/v2/episode/sources?id=${serverId}`;
  const resp = await fetchWithRetry(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest",
    }
  });
  
  if (!resp || !resp.ok) return null;
  
  const data = await resp.json();
  return data.link;
}

async function extractMegacloud(embedUrl) {
  // Simplified - full implementation would need WebCrypto
  const resp = await fetchWithRetry(embedUrl, { headers: MEGACLOUD_HEADERS });
  if (!resp || !resp.ok) return null;
  
  const html = await resp.text();
  
  // Extract client key (simplified)
  const keyMatch = html.match(/([a-zA-Z0-9]{48})/);
  const clientKey = keyMatch ? keyMatch[1] : "anonymous";
  
  // Extract source ID
  const sourceMatch = embedUrl.match(/embed-2\/v3\/e-1\/([a-zA-Z0-9]+)/);
  if (!sourceMatch) return null;
  
  const sourceId = sourceMatch[1];
  
  // Call getSources API
  const apiUrl = `${MEGACLOUD_BASE}/embed-2/v3/e-1/getSources?id=${sourceId}&_k=${clientKey}`;
  const apiResp = await fetchWithRetry(apiUrl, { headers: MEGACLOUD_HEADERS });
  
  if (!apiResp || !apiResp.ok) return null;
  
  return await apiResp.json();
}

async function handleRequest(request) {
  const url = new URL(request.url);
  const slug = url.searchParams.get("slug");
  const episode = parseInt(url.searchParams.get("episode") || "1");
  const search = url.searchParams.get("search");
  
  // CORS headers
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
  };
  
  // Handle CORS preflight
  if (request.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }
  
  // Search endpoint
  if (search) {
    // For search, would need to implement - returning placeholder
    return new Response(JSON.stringify({
      success: false,
      error: "Search not implemented in Workers version"
    }), { headers: corsHeaders });
  }
  
  // Extract endpoint
  if (!slug) {
    return new Response(JSON.stringify({
      success: false,
      error: "Missing slug parameter",
      usage: "?slug=anime-slug&episode=1"
    }), { headers: corsHeaders });
  }
  
  // Extract anime ID from slug
  const match = slug.match(/-(\d+)$/);
  if (!match) {
    return new Response(JSON.stringify({
      success: false,
      error: "Invalid slug format"
    }), { headers: corsHeaders });
  }
  
  const animeId = match[1];
  
  // Get episode ID
  const episodeId = await getEpisodeId(animeId, episode);
  if (!episodeId) {
    return new Response(JSON.stringify({
      success: false,
      error: "Episode not found"
    }), { headers: corsHeaders });
  }
  
  // Get servers
  const servers = await getServers(episodeId);
  if (servers.length === 0) {
    return new Response(JSON.stringify({
      success: false,
      error: "No servers found"
    }), { headers: corsHeaders });
  }
  
  // Find MegaCloud
  let embedUrl = null;
  for (const server of servers) {
    if (server.name.toLowerCase().includes("mega")) {
      const source = await getSource(server.id);
      if (source) {
        embedUrl = source;
        break;
      }
    }
  }
  
  // Fallback to first server
  if (!embedUrl) {
    embedUrl = await getSource(servers[0].id);
  }
  
  if (!embedUrl) {
    return new Response(JSON.stringify({
      success: false,
      error: "No embed URL found"
    }), { headers: corsHeaders });
  }
  
  // Extract M3U8 (simplified)
  const result = await extractMegacloud(embedUrl);
  
  if (!result || !result.sources || result.sources.length === 0) {
    return new Response(JSON.stringify({
      success: false,
      error: "Failed to extract M3U8",
      embed_url: embedUrl,
      note: "Workers version has limited MegaCloud extraction - use server version for full support"
    }), { headers: corsHeaders });
  }
  
  return new Response(JSON.stringify({
    success: true,
    slug,
    episode,
    m3u8_url: result.sources[0].file,
    embed_url: embedUrl,
    episode_id: episodeId,
    intro: result.intro,
    outro: result.outro,
  }), { headers: corsHeaders });
}

addEventListener("fetch", event => {
  event.respondWith(handleRequest(event.request));
});
