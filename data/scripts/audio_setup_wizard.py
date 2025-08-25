"""
Audio Setup Wizard for LAN Screen Streamer
Comprehensive guide for configuring audio with VB-CABLE or Stereo Mix
"""

import sys
import os
import subprocess
import webbrowser

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print a formatted header"""
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()

def enumerate_audio_devices():
    """List all audio devices"""
    if not PYAUDIO_AVAILABLE:
        print("ERROR: PyAudio not installed!")
        print("Please run: pip install pyaudio")
        return None, None
    
    p = pyaudio.PyAudio()
    input_devices = []
    output_devices = []
    
    try:
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            
            if info['maxInputChannels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'rate': int(info['defaultSampleRate'])
                })
            
            if info['maxOutputChannels'] > 0:
                output_devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxOutputChannels'],
                    'rate': int(info['defaultSampleRate'])
                })
    finally:
        p.terminate()
    
    return input_devices, output_devices

def check_audio_status():
    """Check current audio configuration"""
    print_header("CURRENT AUDIO CONFIGURATION")
    
    if not PYAUDIO_AVAILABLE:
        print("⚠ PyAudio is not installed - Audio will be disabled")
        print("\nTo install PyAudio:")
        print("  1. Run: pip install pyaudio")
        print("  2. If that fails, try: pip install pipwin && pipwin install pyaudio")
        print()
        return False
    
    input_devices, output_devices = enumerate_audio_devices()
    
    # Check for audio capture devices
    print("📥 INPUT DEVICES (for capturing audio):")
    print("-" * 40)
    
    stereo_mix_found = False
    vb_cable_found = False
    voicemeeter_found = False
    
    if input_devices:
        for dev in input_devices:
            print(f"  [{dev['index']}] {dev['name']}")
            
            name_lower = dev['name'].lower()
            if 'stereo mix' in name_lower:
                print("      ✅ STEREO MIX FOUND - Can capture system audio!")
                stereo_mix_found = True
            elif 'cable output' in name_lower:
                print("      ✅ VB-CABLE OUTPUT FOUND - Can capture routed audio!")
                vb_cable_found = True
            elif 'voicemeeter' in name_lower:
                print("      ✅ VOICEMEETER FOUND - Advanced routing available!")
                voicemeeter_found = True
    else:
        print("  No input devices found!")
    
    print()
    print("📤 OUTPUT DEVICES (for playback):")
    print("-" * 40)
    
    if output_devices:
        for dev in output_devices:
            print(f"  [{dev['index']}] {dev['name']}")
            
            name_lower = dev['name'].lower()
            if 'cable input' in name_lower:
                print("      ℹ VB-CABLE INPUT - Route apps here to capture")
    else:
        print("  No output devices found!")
    
    print()
    print("AUDIO STATUS SUMMARY:")
    print("-" * 40)
    
    if stereo_mix_found:
        print("✅ Stereo Mix is available - You can capture all system audio")
        return True
    elif vb_cable_found:
        print("✅ VB-CABLE is installed - You can route specific apps")
        return True
    elif voicemeeter_found:
        print("✅ VoiceMeeter is available - Advanced routing possible")
        return True
    else:
        print("⚠ No system audio capture device found")
        print("  You need to enable Stereo Mix or install VB-CABLE")
        return False

def show_stereo_mix_guide():
    """Guide for enabling Stereo Mix"""
    print_header("HOW TO ENABLE STEREO MIX")
    
    print("Stereo Mix allows you to capture all audio playing on your PC.")
    print()
    print("STEPS TO ENABLE:")
    print("-" * 40)
    print("1. Right-click the Speaker icon in system tray")
    print("2. Select 'Sounds' (or 'Sound settings' → 'More sound settings')")
    print("3. Go to the 'Recording' tab")
    print("4. Right-click in empty space")
    print("5. Check both:")
    print("   ☐ Show Disabled Devices")
    print("   ☐ Show Disconnected Devices")
    print()
    print("6. If 'Stereo Mix' appears:")
    print("   - Right-click on it")
    print("   - Select 'Enable'")
    print("   - Right-click again and select 'Set as Default Device'")
    print()
    print("7. If Stereo Mix doesn't appear:")
    print("   - Your sound card may not support it")
    print("   - Try updating your audio drivers")
    print("   - Or use VB-CABLE instead (Option 2)")
    print()
    
    input("Press Enter to open Windows Sound settings...")
    os.system("mmsys.cpl")

def show_vb_cable_guide():
    """Guide for installing and using VB-CABLE"""
    print_header("VB-CABLE INSTALLATION GUIDE")
    
    print("VB-CABLE creates a virtual audio cable for routing audio.")
    print("This gives you precise control over what audio gets streamed.")
    print()
    print("INSTALLATION STEPS:")
    print("-" * 40)
    print("1. Download VB-CABLE from: https://vb-audio.com/Cable/")
    print("2. Extract the ZIP file")
    print("3. Right-click on VBCABLE_Setup_x64.exe")
    print("4. Select 'Run as administrator'")
    print("5. Click Install")
    print("6. RESTART your computer (required!)")
    print()
    print("AFTER INSTALLATION:")
    print("-" * 40)
    print("To stream specific apps:")
    print("1. Go to Windows Settings → System → Sound")
    print("2. Scroll down to 'Advanced'")
    print("3. Click 'App volume and device preferences'")
    print("4. For each app you want to stream:")
    print("   - Set its Output to 'CABLE Input (VB-Audio Virtual Cable)'")
    print("5. The sender will automatically detect 'CABLE Output' for capture")
    print()
    print("To stream ALL audio:")
    print("1. Set 'CABLE Input' as your default playback device")
    print("2. To still hear audio yourself:")
    print("   - Open Sound Control Panel")
    print("   - Go to Recording tab")
    print("   - Right-click 'CABLE Output'")
    print("   - Properties → Listen tab")
    print("   - Check 'Listen to this device'")
    print("   - Select your speakers/headphones")
    print()
    
    choice = input("Open VB-CABLE download page? (y/n): ")
    if choice.lower() == 'y':
        webbrowser.open("https://vb-audio.com/Cable/")

def show_voicemeeter_guide():
    """Guide for VoiceMeeter (advanced)"""
    print_header("VOICEMEETER - ADVANCED AUDIO ROUTING")
    
    print("VoiceMeeter is a virtual audio mixer for advanced users.")
    print("It provides professional-level audio routing and mixing.")
    print()
    print("WHEN TO USE VOICEMEETER:")
    print("-" * 40)
    print("✓ Mix multiple audio sources")
    print("✓ Apply EQ and effects")
    print("✓ Create separate mixes for streaming and monitoring")
    print("✓ Professional streaming setup")
    print()
    print("INSTALLATION:")
    print("-" * 40)
    print("1. Download from: https://vb-audio.com/Voicemeeter/")
    print("2. Choose version:")
    print("   - VoiceMeeter (Basic) - 3 inputs, 2 outputs")
    print("   - VoiceMeeter Banana - 5 inputs, 3 outputs (recommended)")
    print("   - VoiceMeeter Potato - 8 inputs, 5 outputs (advanced)")
    print("3. Install and restart computer")
    print()
    print("BASIC SETUP FOR STREAMING:")
    print("-" * 40)
    print("1. Set Windows default output to 'VoiceMeeter Input'")
    print("2. In VoiceMeeter:")
    print("   - Set A1 to your speakers/headphones")
    print("   - Enable B1 (virtual output)")
    print("3. In Windows Recording devices:")
    print("   - Use 'VoiceMeeter Output' as capture device")
    print()
    
    choice = input("Open VoiceMeeter download page? (y/n): ")
    if choice.lower() == 'y':
        webbrowser.open("https://vb-audio.com/Voicemeeter/")

def test_audio_capture():
    """Test if audio capture is working"""
    print_header("AUDIO CAPTURE TEST")
    
    if not PYAUDIO_AVAILABLE:
        print("Cannot test - PyAudio not installed")
        return
    
    input_devices, _ = enumerate_audio_devices()
    
    # Find best device
    best_device = None
    for dev in input_devices:
        name_lower = dev['name'].lower()
        if any(x in name_lower for x in ['stereo mix', 'cable output', 'voicemeeter']):
            best_device = dev
            break
    
    if not best_device and input_devices:
        # Use default
        p = pyaudio.PyAudio()
        try:
            default_idx = p.get_default_input_device_info()['index']
            for dev in input_devices:
                if dev['index'] == default_idx:
                    best_device = dev
                    break
        except:
            pass
        finally:
            p.terminate()
    
    if not best_device:
        print("No audio input device available for testing")
        return
    
    print(f"Testing device: {best_device['name']}")
    print("Capturing 3 seconds of audio...")
    print()
    
    p = pyaudio.PyAudio()
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=min(2, best_device['channels']),
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            input_device_index=best_device['index']
        )
        
        import numpy as np
        
        print("Monitoring audio levels:")
        print("-" * 40)
        
        for i in range(30):  # 3 seconds
            data = stream.read(1024, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Calculate volume level
            if len(audio_data) > 0:
                max_val = np.max(np.abs(audio_data))
                level = int((max_val / 32768.0) * 50)  # Scale to 50 chars
                bar = "█" * level + "░" * (50 - level)
                print(f"\r[{bar}] {max_val:5d}", end='')
            
            import time
            time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        
        print("\n")
        print("✅ Audio capture is working!")
        
    except Exception as e:
        print(f"❌ Audio capture failed: {e}")
    finally:
        p.terminate()

def main_menu():
    """Main menu for audio setup wizard"""
    while True:
        clear_screen()
        print_header("AUDIO SETUP WIZARD FOR LAN SCREEN STREAMER")
        
        print("This wizard will help you configure audio for streaming.")
        print()
        print("OPTIONS:")
        print("-" * 40)
        print("[1] Check Current Audio Status")
        print("[2] Enable Stereo Mix (Capture ALL audio)")
        print("[3] Install VB-CABLE (Route specific apps)")
        print("[4] VoiceMeeter Guide (Advanced mixing)")
        print("[5] Test Audio Capture")
        print("[6] Quick Fix - Apply audio improvements")
        print("[0] Exit")
        print()
        
        choice = input("Select option [0-6]: ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            clear_screen()
            has_capture = check_audio_status()
            if not has_capture:
                print("\n💡 TIP: Try option 2 or 3 to enable audio capture")
            input("\nPress Enter to continue...")
        elif choice == '2':
            clear_screen()
            show_stereo_mix_guide()
            input("\nPress Enter to continue...")
        elif choice == '3':
            clear_screen()
            show_vb_cable_guide()
            input("\nPress Enter to continue...")
        elif choice == '4':
            clear_screen()
            show_voicemeeter_guide()
            input("\nPress Enter to continue...")
        elif choice == '5':
            clear_screen()
            test_audio_capture()
            input("\nPress Enter to continue...")
        elif choice == '6':
            clear_screen()
            print_header("APPLYING AUDIO FIXES")
            
            # Copy fixed versions
            import shutil
            if os.path.exists('sender_fixed.py'):
                shutil.copy('sender_fixed.py', 'sender.py')
                print("✅ Updated sender with audio fixes")
            if os.path.exists('receiver_fixed.py'):
                shutil.copy('receiver_fixed.py', 'receiver.py')
                print("✅ Updated receiver with audio fixes")
            
            print("\nAudio improvements applied!")
            print("- Better device detection")
            print("- Separate audio/video queues")
            print("- Dynamic sample rate support")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting audio setup wizard...")
    except Exception as e:
        print(f"\nError: {e}")
        input("Press Enter to exit...")
