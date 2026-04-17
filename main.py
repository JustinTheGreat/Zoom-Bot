import asyncio
from playwright.async_api import async_playwright
import datetime
import os
from pynput import keyboard

# --- INTERACTIVE CONFIGURATION ---
print("--- Zoom Bot Setup ---")
MEETING_ID = input("Enter Meeting ID: ").strip()
PASSCODE = input("Enter Passcode: ").strip()
DISPLAY_NAME = input("Enter Display Name: ").strip()
LEAVE_TIME = input("Enter Leave Time (HH:MM, e.g., 19:50): ").strip()
print("----------------------\n")

# Dynamically find the video file in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_PATH = os.path.join(BASE_DIR, "example.y4m")

manual_exit_requested = False

def on_press(key):
    global manual_exit_requested
    try:
        if key == keyboard.KeyCode.from_char('\x07'): # Ctrl+G
            print("\n[!] Ctrl+G detected! Initiating graceful exit...")
            manual_exit_requested = True
    except AttributeError: pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

async def run_zoom_bot():
    global manual_exit_requested
    
    # Basic validation to ensure critical fields aren't empty
    if not MEETING_ID or not LEAVE_TIME:
        print("Error: Meeting ID and Leave Time are required.")
        return

    async with async_playwright() as p:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Launching Browser...")
        browser = await p.chromium.launch(headless=False, args=[
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
            f"--use-file-for-fake-video-capture={VIDEO_PATH}",
        ])
        
        context = await browser.new_context(permissions=["microphone", "camera"])
        page = await context.new_page()
        
        print(f"Navigating to meeting {MEETING_ID}...")
        await page.goto(f"https://zoom.us/wc/join/{MEETING_ID}")

        # 1. Locate Meeting Frame
        target_frame = None
        for _ in range(30):
            for f in page.frames:
                if await f.is_visible("#input-for-name"):
                    target_frame = f
                    break
            if target_frame: break
            await asyncio.sleep(1)

        if not target_frame:
            print("Failed to find Zoom frame. Check your Meeting ID or Internet connection.")
            await browser.close()
            return

        # 2. Join credentials and Mute in Preview
        print(f"Entering credentials as '{DISPLAY_NAME}'...")
        if await target_frame.is_visible("#input-for-pwd"):
            await target_frame.fill("#input-for-pwd", PASSCODE)
        await target_frame.fill("#input-for-name", DISPLAY_NAME)
        
        await asyncio.sleep(3)

        try:
            mute_btn = target_frame.locator('button[aria-label*="mic"], button[aria-label*="audio"], #preview-audio-control-button').first
            if await mute_btn.is_visible():
                label = await mute_btn.get_attribute("aria-label")
                if label and "unmute" not in label.lower():
                    await mute_btn.click(force=True)
                    print("Muted in Preview Room.")
        except: pass

        if await target_frame.is_visible("button.preview-join-button"):
            await target_frame.click("button.preview-join-button")

        # 3. Handle Admittance and Post-Admission Mute
        print("Bot is in transition. Waiting for host to admit...")
        bot_is_in = False
        
        while not bot_is_in and not manual_exit_requested:
            for f in page.frames:
                audio_btn = f.locator("button:has-text('Join Audio by Computer')")
                if await audio_btn.count() > 0:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Admitted! Joining audio...")
                    await audio_btn.click()
                    await asyncio.sleep(4)
                    
                    try:
                        in_mtg_mute = f.locator('button[aria-label*="mute my microphone"]').first
                        if await in_mtg_mute.count() > 0:
                            label = await in_mtg_mute.get_attribute("aria-label")
                            if label and "unmute" not in label.lower():
                                await in_mtg_mute.click(force=True)
                                print("In-meeting mute confirmed.")
                    except: pass
                    bot_is_in = True
                    break
            await asyncio.sleep(2)

        # 4. Stay until LEAVE_TIME or Ctrl+G
        print(f"Bot session active. Target exit: {LEAVE_TIME}")
        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            if now == LEAVE_TIME or manual_exit_requested:
                print("Initiating leave sequence...")
                try:
                    await page.mouse.move(640, 360) 
                    await asyncio.sleep(1)

                    leave_triggered = False
                    for f in page.frames:
                        leave_btn = f.locator('button[aria-label="Leave"], .footer__leave-btn-container button').first
                        if await leave_btn.count() > 0:
                            try:
                                await leave_btn.click(force=True, timeout=3000)
                            except:
                                await leave_btn.dispatch_event("click")
                            
                            await asyncio.sleep(1.5)
                            confirm_btn = f.locator('button:has-text("Leave Meeting"), .zm-btn--danger').first
                            if await confirm_btn.count() > 0:
                                await confirm_btn.click(force=True)
                                print("Left meeting successfully.")
                            leave_triggered = True
                            break

                        wr_leave_btn = f.locator(".leave-btn, button:has-text('Leave')").first
                        if await wr_leave_btn.count() > 0:
                            await wr_leave_btn.click(force=True)
                            print("Exited from waiting room.")
                            leave_triggered = True
                            break
                    
                    if not leave_triggered: print("UI Exit failed, forcing close.")
                except Exception as e:
                    print(f"Exit error: {e}")
                break
            await asyncio.sleep(1)

        await browser.close()
        print("Bot offline.")
        
if __name__ == "__main__":
    try:
        asyncio.run(run_zoom_bot())
    except KeyboardInterrupt:
        print("\nBot stopped manually.")