#!/usr/bin/env python3
"""
Bed Remote Server — Windows

QUICK START:
  1. Run: python server_windows.py
  2. Open the URL shown on your iPhone's Safari
  3. Control your laptop from your phone!

OPTIONAL (for better volume control):
  pip install pycaw comtypes

REQUIREMENTS:
  - Windows with Python 3
  - Both devices on same WiFi
"""

import http.server
import json
import subprocess
import urllib.parse
import os
import socketserver
import socket
import ctypes
import time

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

# Windows key codes
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_LEFT = 0x25
VK_RIGHT = 0x27
VK_SPACE = 0x20
VK_F = 0x46

# Load pycaw for volume control
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    import math

    def _get_volume_interface():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))

    def get_volume():
        vol = _get_volume_interface()
        level = vol.GetMasterVolumeLevelScalar()
        return int(round(level * 100))

    def set_volume_level(percent):
        vol = _get_volume_interface()
        vol.SetMasterVolumeLevelScalar(percent / 100.0, None)
        return percent

    PYCAW_AVAILABLE = True
    print("  ✓ pycaw loaded — using precise volume control")

except ImportError:
    PYCAW_AVAILABLE = False
    print("  ⚠ pycaw not found — using keyboard keys for volume (install pycaw for precise control)")

    def get_volume():
        return 50  # fallback

    def set_volume_level(percent):
        return percent


def send_key(vk_code):
    """Simulate a key press using Windows API."""
    KEYEVENTF_KEYUP = 0x0002
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


# ====================================
# COMMAND HANDLERS
# Each function handles one button press from the phone
# ====================================

def cmd_playpause():
    """Play/Pause: Sends spacebar key"""
    send_key(VK_SPACE)
    return {"ok": True}


def cmd_vol_up():
    if PYCAW_AVAILABLE:
        v = get_volume()
        new_v = set_volume_level(min(100, v + 10))
    else:
        send_key(VK_VOLUME_UP)
        send_key(VK_VOLUME_UP)
        new_v = get_volume()
    return {"ok": True, "volume": new_v}


def cmd_vol_down():
    if PYCAW_AVAILABLE:
        v = get_volume()
        new_v = set_volume_level(max(0, v - 10))
    else:
        send_key(VK_VOLUME_DOWN)
        send_key(VK_VOLUME_DOWN)
        new_v = get_volume()
    return {"ok": True, "volume": new_v}


def cmd_mute():
    send_key(VK_VOLUME_MUTE)
    return {"ok": True, "volume": 0}


def cmd_skip_forward():
    send_key(VK_RIGHT)
    return {"ok": True}


def cmd_skip_back():
    send_key(VK_LEFT)
    return {"ok": True}


def cmd_lock():
    ctypes.windll.user32.LockWorkStation()
    return {"ok": True}


def cmd_fullscreen():
    send_key(VK_F)
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

        if path == '/' or path == '/index.html':
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
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
            self.send_json({'ok': True, 'platform': 'windows', 'volume': v})
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
    print(f"  ║  Platform : Windows                    ║")
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
