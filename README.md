# 🖥️ LAN Screen Streamer v1.0

<div align="center">
  <img src="https://img.shields.io/badge/version-1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  
  **Developed with ❤️ by Kishnanda - For Streamers, By Streamers**
</div>

[➡ Installation and Quick Use Guide](INSTALLATION.md)

## 🌟 What is LAN Screen Streamer?

**LAN Screen Streamer** is a simple yet powerful tool designed primarily for PC-to-PC dual streaming on your local network - no internet required. Perfect for:

- 🖥️🖥️ Dual-PC streaming: send your desktop to a second PC running OBS, which streams online
- 📺 Stream your PC to your TV
- 🎮 Share gameplay with friends in the same room
- 📊 Present wirelessly in meetings
- 🎬 Watch movies from your PC on any device
- 👨‍🏫 Teaching and demonstrations

## ✨ Features

- 🚀 **One-Click Setup** - Just double-click to start!
- 🔊 **Audio Support** - Stream both video AND sound
- 💾 **Auto-Save Settings** - Remembers your preferences
- 🎯 **Smart Connection** - Automatically finds devices
- 🖥️🖥️ **PC-to-PC (Dual Streaming)** - Built for dual-PC workflows; pair with OBS on the receiver PC for online streaming
- 🔒 **Secure** - Only works on your local network
- ⚡ **Low Latency** - Near real-time streaming

## 📋 Requirements

### For Everyone (Non-Technical Users)
- ✅ Windows 10 or Windows 11
- ✅ Two devices on the same WiFi/Network
- ✅ That's it! Everything else is handled automatically

### For Technical Users
- Python 3.8 or higher (auto-installed if missing)
- Required packages (auto-installed):
  - opencv-python
  - numpy
  - Pillow
  - dxcam (screen capture)
  - mss (fallback capture)
  - sounddevice
  - pyaudio

## 🚀 Quick Start Guide

### Step 1: Download
1. Click the green **"Code"** button above
2. Select **"Download ZIP"**
3. Extract the ZIP file to any folder

### Step 2: Start Streaming
1. **Double-click** `LAN_Streamer_1.0.bat`
2. Choose your role:
   - Press **1** to share YOUR screen (Sender)
   - Press **2** to watch SOMEONE ELSE'S screen (Receiver)
3. Follow the simple on-screen instructions!

### That's it! 🎉 You're streaming!

## 📖 Detailed Usage

### 🖥️ To Share Your Screen (Sender PC)
1. Run `LAN_Streamer_1.0.bat`
2. Press **1** for Sender mode
3. Enter the Receiver PC's IP (shown on the Receiver screen)
4. Choose resolution and quality when prompted
5. Your screen is now being streamed
6. Press **Q** to stop streaming

### 🖥️ To Receive a Stream (Receiver PC)
1. Run `LAN_Streamer_1.0.bat`
2. Press **2** for Receiver mode
3. Choose an audio output device (or press Enter for default)
4. You'll see a waiting screen with this PC's IP — give this IP to the Sender
5. Enjoy the stream (press **F** for fullscreen)
6. Press **Q** or **ESC** to stop watching

### 🎥 Dual-PC streaming with OBS (PC-to-PC -> OBS -> online)
On the streaming PC (Receiver) where OBS is installed:
1. Start Receiver (option 2) and ensure the "LAN Stream HD" window is visible.
2. In OBS, add a source:
   - Window Capture: select the "LAN Stream HD" window; or
   - Display Capture: capture the monitor showing the receiver window.
3. Ensure audio is captured in OBS:
   - Use Desktop Audio; or
   - Add a WASAPI capture of your chosen output device.
4. Go Live in OBS to stream to your platform.

## 🎯 Pro Tips

### For Best Performance:
- 🌐 Use 5GHz WiFi when possible
- 🔌 Ethernet cable gives the smoothest experience
- 🖥️ Close unnecessary programs while streaming
- 📺 Full-screen mode: Press **F** while watching

### Keyboard Shortcuts:
- **Q** - Quit/Stop streaming
- **F** - Toggle fullscreen (Receiver only)
- **Space** - Pause/Resume (Receiver only)
- **+/-** - Adjust volume (Receiver only)

## 🔧 Troubleshooting

### "It's not working!" - Don't panic! Try these:

1. **Both devices on same network?**
   - Check if both devices are connected to the same WiFi
   - Try pinging the other device

2. **Firewall blocking?**
   - Windows Defender may ask for permission - click "Allow"
   - Temporarily disable firewall to test

3. **Black screen?**
   - Run as Administrator
   - Check if antivirus is blocking screen capture

4. **No audio?**
   - Run audio setup: Choose option 3 in main menu
   - Check Windows audio settings
   - Make sure audio device is not muted

5. **Connection refused?**
   - Check the IP address is correct
   - Make sure sender started first
   - Try restarting both applications

## 📁 Project Structure

```
LAN-Streamer-Project/
│
├── LAN_Streamer_1.0.bat     # Main launcher - double-click this!
│
└── data/                     # Application data (don't modify!)
    ├── scripts/              # Core Python scripts
    ├── config/               # Saved settings
    └── logs/                 # Error logs for troubleshooting
```

## 🤝 Contributing

We love contributions! Whether you're fixing bugs, adding features, or improving documentation:

1. Fork this repository
2. Create your feature branch (`git checkout -b amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ using Python
- OpenCV for video processing
- DXCam for high-performance screen capture
- Community contributors
- **Developed with ❤️ by Kishnanda - For Streamers, By Streamers**

## 💬 Support

Having issues? We're here to help!

- 📧 Open an [Issue](https://github.com/yourusername/LAN-Streamer-Project/issues)
- 💡 Check our [Wiki](https://github.com/yourusername/LAN-Streamer-Project/wiki)
- 🤔 Read the [FAQ](#frequently-asked-questions)

## ❓ Frequently Asked Questions

**Q: Do I need internet?**
A: No! This works entirely on your local network.

**Q: Can I stream to multiple devices?**
A: Currently supports one-to-one streaming. Multi-cast coming soon!

**Q: Is it secure?**
A: Yes! Only devices on your local network can connect.

**Q: Why is it laggy?**
A: Check your network speed and try reducing quality in settings.

**Q: Can I stream games?**
A: Yes! Though fast-paced games may have slight delay.

**Q: Works on Mac/Linux?**
A: Currently Windows only. Mac/Linux support planned!

---

<div align="center">
  
  **Developed with ❤️ by Kishnanda - For Streamers, By Streamers**
  
  ⭐ Star this repo if you find it helpful!
</div>
