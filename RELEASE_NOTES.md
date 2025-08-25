# LAN Screen Streamer v1.0.0 — Release Notes

What’s new
- First public release of LAN Screen Streamer for Windows
- One‑click launcher (LAN_Streamer_1.0.bat) with Sender/Receiver modes
- Low‑latency JPEG video streaming over LAN
- Audio capture/playback with device selection (PyAudio)
- Smart settings persistence (IP history, resolution, quality, audio device)
- Setup wizard and system checks for a smoother first‑run experience
- Clear INSTALLATION.md with non‑technical, step‑by‑step guidance

Quick start
1) On both PCs, right‑click setup.bat → Run as administrator (let it finish; if it errors, run it again).
2) On the display PC (Receiver): Run LAN_Streamer_1.0.bat → type 2 → choose audio (or press Enter).
3) On the sharing PC (Sender): Run LAN_Streamer_1.0.bat → type 1 → enter Receiver IP → choose resolution/quality.
4) Tip: Press F on the Receiver to toggle fullscreen for smoother playback.

Requirements
- Windows 10/11, both PCs on the same network
- Python 3.8+ (setup.bat installs dependencies automatically)

Known limitations
- One‑to‑one streaming for now (multi‑viewer planned)
- Windows only in this version

Credits
- Developed with ❤️ by Kishnanda — For Streamers, By Streamers.

