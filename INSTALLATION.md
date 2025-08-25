# LAN Screen Streamer – Installation and Quick Use Guide

Audience: non-technical users who just want this to work.
Platform: Windows 10/11

Before you start
- Make sure both PCs are on the same local network (same Wi‑Fi or same router).
- Close heavy apps for smoother performance.

Step 1 — Run setup as Administrator
1) Right‑click setup.bat and choose “Run as administrator”.
2) Follow the on‑screen instructions. If something seems to break during install, let it finish, then simply run Step 1 again (2–3 times if needed).
3) Repeat Step 1 on your second PC as well.

Step 2 — Start the Receiver (the PC that will display the stream)
1) Double‑click LAN_Streamer_1.0.bat.
2) Type 2 to select Receiver.
3) When prompted, pick an audio output device (or just press Enter to use the default). You’ll see a “waiting…” message with this PC’s IP address.

Step 3 — Start the Sender (the PC that will share its screen)
1) Double‑click LAN_Streamer_1.0.bat.
2) Type 1 to select Sender.
3) Enter the Receiver’s IP (shown on the other PC).
4) Choose your desired resolution and quality.
5) That’s it — streaming starts.

Tips for smoother playback (Receiver side)
- When the stream is active, make the player window fullscreen (press F). This reduces distractions and can improve smoothness.

Common issues and quick fixes
- Can’t connect: Ensure both PCs are on the same network and the Receiver is already running. If Windows Firewall prompts appear, click Allow.
- Black screen or no capture: Try running as Administrator. Update your graphics drivers.
- No audio: Run the Audio Setup (option 3 in the main menu) or make sure your audio device isn’t muted.

Uninstall/cleanup
- No formal installer is used. To remove, just delete the project folder. Your settings live in data/config/stream_config.json and are ignored by Git — you can delete them if you want a fresh start.

Credits
- Developed with ❤️ by Kishnanda — For Streamers, By Streamers.

