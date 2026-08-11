#!/usr/bin/env python3
"""
Venice Lagoon eBird Proxy
Reads EBIRD_API_KEY from ~/.hermes/territory/tokens.json
Fetches recent bird observations for the Venice Lagoon area
Caches for 15 minutes, serves on HTTP endpoint

Usage: python3 ebird_proxy.py [--port 8766]

Place on vlmars and run persistently. Add nginx:
  location /api/ebird {
      proxy_pass http://127.0.0.1:8766/observations;
      proxy_http_version 1.1;
  }
"""

import json, os, time, sys, argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

# Venice Lagoon bounding box
LAT, LNG, DIST = 45.44, 12.33, 20  # km radius

# Cache
cache = {"data": None, "ts": 0, "ttl": 900}  # 15 min TTL

def get_api_key():
    """Read EBIRD_API_KEY from tokens.json"""
    tokens_path = os.path.expanduser("~/.hermes/territory/tokens.json")
    if os.path.exists(tokens_path):
        with open(tokens_path) as f:
            tokens = json.load(f)
        return tokens.get("EBIRD_API_KEY", "")
    return os.environ.get("EBIRD_API_KEY", "")

def fetch_ebird():
    """Fetch recent bird observations within radius of Venice Lagoon"""
    now = time.time()
    if cache["data"] and (now - cache["ts"]) < cache["ttl"]:
        return cache["data"]
    
    api_key = get_api_key()
    if not api_key:
        return {"error": "No EBIRD_API_KEY configured", "observations": []}
    
    url = f"https://api.ebird.org/v2/data/obs/geo/recent?lat={LAT}&lng={LNG}&dist={DIST}&back=7"
    req = Request(url, headers={"X-eBirdApiToken": api_key})
    
    try:
        resp = urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        # Transform to simple format
        birds = []
        for obs in data[:25]:
            birds.append({
                "name": obs.get("comName", ""),
                "sciName": obs.get("sciName", ""),
                "count": obs.get("howMany", 1),
                "lat": obs.get("lat"),
                "lng": obs.get("lng"),
                "date": obs.get("obsDt", ""),
                "loc": obs.get("locName", ""),
            })
        
        result = {"observations": birds, "cached_at": now, "source": "ebird"}
        cache["data"] = json.dumps(result)
        cache["ts"] = now
        return cache["data"]
    except URLError as e:
        return {"error": str(e), "observations": []}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/observations', '/'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(fetch_ebird().encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            key_status = "configured" if get_api_key() else "missing"
            self.wfile.write(f"OK (ebird key: {key_status})".encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    
    server = HTTPServer(('127.0.0.1', args.port), Handler)
    key = get_api_key()
    print(f"eBird proxy on :{args.port} (key: {'configured' if key else 'MISSING'})")
    print(f"Area: {LAT},{LNG} ±{DIST}km")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == '__main__':
    main()
