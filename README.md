# 🛏️ Bed Remote

**Control your laptop from your phone while watching Netflix/Disney+ in bed.**

## 🚀 Quick Start

### macOS
```bash
cd /path/to/this/folder
python3 server_mac.py
```

### Windows
```cmd
cd C:\path\to\this\folder
python server_windows.py
```

**Then:** Open the URL shown in your terminal on your iPhone's Safari browser.

**Optional:** Tap Share → Add to Home Screen for a native app experience.

---

## 📱 What You Get

| Button | Action |
|--------|--------|
| ⏸ **Play/Pause** | Space bar |
| ⏪ **Back 10s** | Left arrow |
| ⏩ **Forward 10s** | Right arrow |
| 🔊/🔉 **Volume** | System volume ±10% |
| 🔇 **Mute** | Toggle mute |
| ⛶ **Fullscreen** | F key |
| 🔒 **Lock** | Lock your laptop |

Works with Netflix, Disney+, YouTube, and most video players in your browser.

---

## ⚠️ Security Notice

**No authentication!** Anyone on your WiFi can control your laptop if they find the URL.

✅ **Safe:** Home WiFi you trust  
❌ **Don't use:** Coffee shops, airports, hotels, dorms

*See code comments for adding password protection.*

---

## 📋 Requirements

- **Python 3** (pre-installed on Mac, [download for Windows](https://python.org))
- **Same WiFi network** for phone and laptop
- **Safari** on iPhone (for Add to Home Screen feature)

---

## 🖥️ Detailed Setup

### macOS

**Step 1:** Open Terminal and navigate to this folder
```bash
cd /path/to/Mobile_Remote
```

**Step 2:** Grant keyboard permissions  
Go to: **System Preferences → Privacy & Security → Accessibility**  
Add **Terminal** to the allowed list.

**Step 3:** Run the server
```bash
python3 server_mac.py
```

**Step 4:** Open the URL on your iPhone  
You'll see something like `http://192.168.1.42:8765` — open that in Safari.

**Step 5 (Optional):** Add to Home Screen  
Safari → Share (box with arrow) → Add to Home Screen

---

### Windows

**Step 1:** Open Command Prompt
```cmd
cd C:\Users\YourName\Downloads\Mobile_Remote
```

**Step 2 (Optional):** Better volume control
```cmd
pip install pycaw comtypes
```
Skip this and volume will still work with keyboard keys.

**Step 3:** Run the server
```cmd
python server_windows.py
```

**Step 4:** Allow firewall access  
Click **Allow access** when Windows Defender asks.

**Step 5:** Open the URL on your iPhone  
Check the terminal for your URL, open in Safari.

**Step 6 (Optional):** Add to Home Screen  
Safari → Share → Add to Home Screen

---

## 💡 Tips

- Works best with Netflix and Disney+ in your browser
- For fullscreen: click the video player first, then press ⛶
- Server must keep running on your laptop
- Volume controls affect system-wide audio

---

## ❓ Troubleshooting

**Can't connect from iPhone?**
- Check server is running on laptop
- Verify both devices on same WiFi network
- On Windows: allow through Firewall when prompted

**Keys not working on Mac?**
- Add Terminal to System Preferences → Privacy → Accessibility

**Fullscreen doesn't work?**
- Click the browser/player window first
- Then use the ⛶ button

---

## 🛠️ Files

```
index.html        → Phone interface (web app)
server_mac.py     → macOS server
server_windows.py → Windows server
README.md         → This guide
```
