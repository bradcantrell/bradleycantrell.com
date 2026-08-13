#!/usr/bin/env python3
"""
Venice Lagoon AIS Bridge
Connects to aisstream.io WebSocket, subscribes to Venice Lagoon bounding box,
serves active vessel positions on HTTP endpoint for the territory map.

Usage: python venice_ais_bridge.py --api-key YOUR_KEY [--port 8765]
"""

import asyncio
import json
import time
import argparse
import signal
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import websockets
except ImportError:
    print("websockets not installed. Run: pip install websockets")
    sys.exit(1)

# Venice Lagoon bounding box
VENICE_BBOX = [[[44.0, 12.0], [46.0, 14.0]]]  # Wide: covers lagoon + approach corridor + Trieste

# Store latest vessel positions
vessels = {}  # mmsi -> {lat, lng, heading, speed, name, timestamp}
last_update = time.time()

class VesselHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/vessels':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            # Only return vessels updated in last 10 minutes
            now = time.time()
            active = {k: v for k, v in vessels.items() if now - v.get('ts', 0) < 600}
            self.wfile.write(json.dumps({
                'count': len(active),
                'vessels': list(active.values()),
                'updated': last_update
            }).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f'OK {len(vessels)} vessels'.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # quiet

async def connect_ais(api_key):
    global vessels, last_update
    url = "wss://stream.aisstream.io/v0/stream"
    
    while True:
        try:
            print(f"[AIS] Connecting to {url}...")
            async with websockets.connect(url, ping_interval=30) as ws:
                # Subscribe
                sub = {
                    "APIKey": api_key,
                    "BoundingBoxes": VENICE_BBOX,
                    "FilterMessageTypes": ["PositionReport", "ShipStaticData"]
                }
                await ws.send(json.dumps(sub))
                print(f"[AIS] Subscribed to Venice Lagoon {VENICE_BBOX}")
                
                async for msg in ws:
                    try:
                        data = json.loads(msg)
                        msg_type = data.get("MessageType", "")
                        body = data.get("Message", {})
                        pr = body.get("PositionReport", {})
                        sd = body.get("ShipStaticData", {})
                        
                        # MMSI is in UserID field
                        mmsi = ""
                        if msg_type == "PositionReport":
                            mmsi = str(pr.get("UserID", ""))
                        elif msg_type == "ShipStaticData":
                            mmsi = str(sd.get("UserID", ""))
                        if not mmsi:
                            continue
                        
                        entry = vessels.get(mmsi, {"mmsi": mmsi, "name": "", "lat": 0, "lng": 0, "heading": 0, "speed": 0})
                        entry["ts"] = time.time()
                        
                        if msg_type == "PositionReport":
                            lat = pr.get("Latitude", 0)
                            lng = pr.get("Longitude", 0)
                            if not lat or not lng:
                                continue
                            entry["lat"] = lat
                            entry["lng"] = lng
                            entry["heading"] = pr.get("TrueHeading", 0)
                            entry["speed"] = pr.get("Sog", 0)
                            entry["cog"] = pr.get("Cog", 0)
                            entry["status"] = pr.get("NavigationalStatus", 0)
                            
                        elif msg_type == "ShipStaticData":
                            name = sd.get("Name", "")
                            callsign = sd.get("CallSign", "")
                            dest = sd.get("Destination", {})
                            if name: entry["name"] = name
                            if callsign: entry["callsign"] = callsign
                            if dest and isinstance(dest, dict):
                                c = dest.get("Country", "")
                                l = dest.get("Locode", "")
                                if c or l: entry["destination"] = f"{c}/{l}"
                        
                        vessels[mmsi] = entry
                        
                    except Exception as e:
                        pass  # skip malformed messages
                
                last_update = time.time()
                
        except Exception as e:
            print(f"[AIS] Connection error: {e}, retrying in 5s...")
            await asyncio.sleep(5)

async def main_async(api_key, port):
    # Start HTTP server in thread
    server = HTTPServer(('127.0.0.1', port), VesselHandler)
    print(f"[HTTP] Vessel endpoint: http://127.0.0.1:{port}/vessels")
    
    import threading
    http_thread = threading.Thread(target=server.serve_forever, daemon=True)
    http_thread.start()
    
    # Connect to AIS stream
    await connect_ais(api_key)

def main():
    parser = argparse.ArgumentParser(description='Venice Lagoon AIS Bridge')
    parser.add_argument('--api-key', required=True, help='aisstream.io API key')
    parser.add_argument('--port', type=int, default=8765, help='HTTP server port')
    args = parser.parse_args()
    
    try:
        asyncio.run(main_async(args.api_key, args.port))
    except KeyboardInterrupt:
        print("\n[AIS] Shutting down...")

if __name__ == '__main__':
    main()
