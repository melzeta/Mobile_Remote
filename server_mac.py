#!/usr/bin/env python3
"""
Bed Remote Server — macOS

QUICK START:
  1. Run: python3 server_mac.py
  2. Open the URL shown on your iPhone's Safari
  3. Control your laptop from your phone!

REQUIREMENTS:
  - macOS with Python 3
  - Both devices on same WiFi
  - Terminal added to Accessibility permissions
"""

import http.server
import json
import subprocess
import urllib.parse
import os
import socketserver
import socket

PORT = 8765

# ⚠️ SECURITY WARNING: This server has NO AUTHENTICATION!
# Anyone on your network can control your laptop.
# 
# TODO: Implement authentication before using on shared networks:
# 1. Add a password/PIN requirement
# 2. Use HTTPS with SSL certificates
# 3. Implement token-based authentication
# 4. Add rate limiting to prevent abuse
#
# Example: Uncomment and modify this to require a simple password:
# REQUIRED_PASSWORD = "your-secure-password-here"

def get_local_ip():
    """Get the Mac's local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def run_apple_script(script):
    """Run an AppleScript command."""
    subprocess.run(['osascript', '-e', script], check=False)

def get_volume():
    """Get current system volume (0-100)."""
    result = subprocess.run(
        ['osascript', '-e', 'output volume of (get volume settings)'],
        capture_output=True, text=True
    )
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 50

def set_volume(level):
    """Set system volume (0-100)."""
    level = max(0, min(100, level))
    run_apple_script(f'set volume output volume {level}')
    return level

# ====================================
# COMMAND HANDLERS
# Each function handles one button press from the phone
# ====================================

def cmd_playpause():
    """Play/Pause: Sends spacebar key"""
    run_apple_script('tell application "System Events" to key code 49')  # spacebar
    return {"ok": True}

def cmd_vol_up():
    v = get_volume()
    new_v = set_volume(v + 10)
    return {"ok": True, "volume": new_v}

def cmd_vol_down():
    v = get_volume()
    new_v = set_volume(v - 10)
    return {"ok": True, "volume": new_v}

def cmd_mute():
    run_apple_script('set volume with output muted')
    return {"ok": True, "volume": 0}

def cmd_skip_forward():
    # Sends Right arrow key (works in most video players and browsers)
    run_apple_script('tell application "System Events" to key code 124')  # right arrow
    return {"ok": True}

def cmd_skip_back():
    # Sends Left arrow key
    run_apple_script('tell application "System Events" to key code 123')  # left arrow
    return {"ok": True}

def cmd_lock():
    """Lock the screen."""
    subprocess.run([
        'osascript', '-e',
        'tell application "System Events" to keystroke "q" using {command down, control down}'
    ], check=False)
    return {"ok": True}

def cmd_fullscreen():
    """Toggle fullscreen (Ctrl+Command+F)."""
    run_apple_script(
        'tell application "System Events" to keystroke "f" using {command down, control down}'
    )
    return {"ok": True}

# Map phone button names to handler functions
COMMANDS = {
    'playpause': cmd_playpause,      # ⏸ button
    'vol_up': cmd_vol_up,            # 🔊 button
    'vol_down': cmd_vol_down,        # 🔉 button
    'mute': cmd_mute,                # 🔇 button
    'skip_forward': cmd_skip_forward,# ⏩ button
    'skip_back': cmd_skip_back,      # ⏪ button
    'lock': cmd_lock,                # 🔒 button
    'fullscreen': cmd_fullscreen,    # ⛶ button
}

class RemoteHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"  [{self.address_string()}] {format % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        # Allow iPhone on local network
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        # Serve the remote UI
        if path == '/' or path == '/index.html':
            html_path = os.path.join(os.path.dirname(__file__), 'index.html')
            if os.path.exists(html_path):
                with open(html_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_json({'error': 'index.html not found — put it in the same folder'}, 404)

        elif path == '/status':
            v = get_volume()
            self.send_json({'ok': True, 'platform': 'mac', 'volume': v})
        else:
            self.send_json({'error': 'not found'}, 404)

    def do_POST(self):
        # TODO: Add authentication check here
        # Example:
        # auth_header = self.headers.get('Authorization')
        # if not auth_header or auth_header != f"Bearer {REQUIRED_PASSWORD}":
        #     self.send_json({'error': 'unauthorized'}, 401)
        #     return
        
        path = urllib.parse.urlparse(self.path).path
        parts = path.strip('/').split('/')

        if len(parts) == 2 and parts[0] == 'cmd':
            cmd_name = parts[1]
            if cmd_name in COMMANDS:
                try:
                    result = COMMANDS[cmd_name]()
                    self.send_json(result)
                    print(f"  ✓ {cmd_name}")
                except Exception as e:
                    self.send_json({'error': str(e)}, 500)
            else:
                self.send_json({'error': f'unknown command: {cmd_name}'}, 400)
        else:
            self.send_json({'error': 'not found'}, 404)


class ThreadedServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == '__main__':
    ip = get_local_ip()
    print()
    print("  ╔════════════════════════════════════════╗")
    print("  ║         🛏️  Bed Remote Server           ║")
    print("  ╠════════════════════════════════════════╣")
    print(f"  ║  Platform : macOS                      ║")
    print(f"  ║  Running  : http://{ip}:{PORT}  ║")
    print(f"  ║                                        ║")
    print(f"  ║  Open this on your iPhone:             ║")
    print(f"  ║  http://{ip}:{PORT}           ║")
    print(f"  ║                                        ║")
    print(f"  ║  Tip: Add to Home Screen in Safari     ║")
    print(f"  ║  for a full-screen app experience!     ║")
    print("  ╚════════════════════════════════════════╝")
    print()
    print("  Press Ctrl+C to stop.")
    print()

    server = ThreadedServer(('0.0.0.0', PORT), RemoteHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
