# 📷 Zoom-Bot
A browser-based (Chromium) Zoom automation tool built with Python and Playwright. This bot joins meetings via the web client, handles credentials, mutes audio on entry, and streams a local video file on loop (`.y4m`) as a virtual camera.

## ✨ Features
* **Virtual Webcam:** Streams a local `.y4m` video file as your camera feed on loop.
* **Auto-Mute:** Automatically mutes in the preview room and after joining the meeting.
* **Scheduled Exit:** Leaves the meeting automatically at a user-defined time.
* **Manual Override:** Use `Ctrl+G` to trigger exit the meeting.

---

## 🛠️ Installation

### 1. Prerequisite: Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

```bash
python -m venv .venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install Python Dependencies
```bash
pip install playwright pynput
playwright install chromium
```

### 3. Linux-Specific Setup
If you are running on a Linux distribution (e.g., Ubuntu, Debian), you must install the necessary system libraries for Chromium to run:

```bash
sudo playwright install-deps
```
*Note: If you are running on a server without a display (headless), ensure you have `Xvfb` installed if you intend to run the browser with `headless=False`.*

---

## 🚀 Usage

1. **Prepare your Video:** Place a video file named `example.y4m` in the same directory as `main.py`.
   * *Tip: To convert an MP4 to Y4M using FFmpeg:* `ffmpeg -i input.mp4 output.y4m`
2. **Run the Script:**
   ```bash
   python main.py
   ```
3. **Configure the Bot:** Follow the terminal prompts to enter the Meeting ID, Passcode, Display Name, and Leave Time (24-hour format, e.g., `19:50`).

---

## ⌨️ Controls
* **Ctrl+G:** Triggers a "Graceful Exit." The bot will attempt to click the "Leave Meeting" buttons in the Zoom interface before closing.
* **Ctrl+C:** Force-stop the script in the terminal.

## ⚠️ Disclaimer
This tool is for educational purposes. Ensure you comply with Zoom's Terms of Service and local privacy laws regarding automated meeting attendance.
