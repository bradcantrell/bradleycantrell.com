# AIS Bridge Service for vlmars
# Run this on vlmars to provide vessel data:
#
#   python3 /infrastructure/www/venice-studio/venice_ais_bridge.py --api-key YOUR_KEY --port 8765
#
# Then add this nginx location block:
#
#   location /ais/vessels {
#       proxy_pass http://127.0.0.1:8765/vessels;
#       proxy_http_version 1.1;
#       proxy_set_header Host $host;
#   }
#
# Map auto-detects: when on bradleycantrell.com → /ais/vessels
# From GitHub Pages → http://100.81.134.59/ais/vessels
