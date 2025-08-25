"""
LAN Screen Sender - Enhanced with Smart Settings Management
Intuitive UX with memory for quick reconnect and flexible configuration
"""
import sys
import socket
import struct
import time
import cv2
import numpy as np
import threading
import queue
import json
import os
import argparse
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from settings_manager import get_settings

try:
    import dxcam
except ImportError:
    print("ERROR: dxcam not installed! Run: pip install dxcam")
    sys.exit(1)

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    print("WARNING: PyAudio not installed! Audio will be disabled.")
    print("To enable audio, run: pip install pyaudio")
    AUDIO_AVAILABLE = False
    pyaudio = None

# Remove old ConnectionConfig class - now using SettingsManager

class DualNetworkSender:
    """Network sender with separate queues for video and audio"""
    def __init__(self, sock):
        self.sock = sock
        self.video_queue = queue.Queue(maxsize=5)  # Smaller for lower latency
        self.audio_queue = queue.Queue(maxsize=30)  # Larger for audio buffering
        self.stop_event = threading.Event()
        self.stats = {'video_sent': 0, 'audio_sent': 0, 'video_dropped': 0, 'audio_dropped': 0}
        self.thread = threading.Thread(target=self._sender_thread)
        self.thread.start()
    
    def _sender_thread(self):
        """Background thread that prioritizes audio over video"""
        while not self.stop_event.is_set():
            try:
                # Always check audio queue first (priority)
                try:
                    audio_data = self.audio_queue.get_nowait()
                    self.sock.sendall(audio_data)
                    self.stats['audio_sent'] += 1
                    continue  # Process more audio if available
                except queue.Empty:
                    pass
                
                # Then check video queue
                try:
                    video_data = self.video_queue.get(timeout=0.01)
                    self.sock.sendall(video_data)
                    self.stats['video_sent'] += 1
                except queue.Empty:
                    pass
                    
            except Exception as e:
                print(f"Send error: {e}")
                break
    
    def send_video(self, data):
        """Queue video data for sending"""
        try:
            self.video_queue.put_nowait(data)
            return True
        except queue.Full:
            self.stats['video_dropped'] += 1
            return False  # Drop frame if queue is full
    
    def send_audio(self, data):
        """Queue audio data for sending (priority)"""
        try:
            self.audio_queue.put_nowait(data)
            return True
        except queue.Full:
            # For audio, try to make room by dropping oldest
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put_nowait(data)
                self.stats['audio_dropped'] += 1
                return True
            except:
                return False
    
    def get_stats(self):
        """Get transmission statistics"""
        return self.stats.copy()
    
    def stop(self):
        """Stop the sender thread"""
        self.stop_event.set()
        self.thread.join(timeout=1)

def enumerate_audio_devices():
    """Enumerate all audio input devices"""
    if not AUDIO_AVAILABLE:
        return []
    
    p = pyaudio.PyAudio()
    devices = []
    
    try:
        print("\n=== Available Audio Input Devices ===")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'rate': int(info['defaultSampleRate']),
                    'is_default': i == p.get_default_input_device_info()['index']
                })
                status = " [DEFAULT]" if devices[-1]['is_default'] else ""
                print(f"  [{i}] {info['name']} ({info['maxInputChannels']} ch, {int(info['defaultSampleRate'])} Hz){status}")
    except Exception as e:
        print(f"Error enumerating devices: {e}")
    finally:
        p.terminate()
    
    return devices

def select_audio_device():
    """Select the best audio device or let user choose"""
    if not AUDIO_AVAILABLE:
        return None
    
    devices = enumerate_audio_devices()
    if not devices:
        print("ERROR: No audio input devices found!")
        return None
    
    # Priority order for automatic selection
    priority_keywords = [
        'cable output',  # VB-Cable
        'stereo mix',     # Stereo Mix
        'what u hear',    # Some soundcards use this
        'loopback',       # Generic loopback
        'vb-audio',       # Any VB-Audio device
        'voicemeeter',    # VoiceMeeter outputs
    ]
    
    # Try to find a preferred device
    selected = None
    for keyword in priority_keywords:
        for device in devices:
            if keyword in device['name'].lower():
                selected = device
                print(f"\n✓ Auto-selected: {device['name']}")
                break
        if selected:
            break
    
    # If no preferred device, check for default
    if not selected:
        for device in devices:
            if device['is_default']:
                selected = device
                print(f"\n✓ Using default device: {device['name']}")
                break
    
    # If still no device, ask user
    if not selected:
        print("\nNo preferred audio device found.")
        print("Enter device number from list above (or press Enter to skip audio): ")
        choice = input().strip()
        
        if choice:
            try:
                idx = int(choice)
                for device in devices:
                    if device['index'] == idx:
                        selected = device
                        print(f"✓ Selected: {device['name']}")
                        break
            except:
                print("Invalid selection, audio disabled")
                return None
        else:
            print("Audio capture disabled")
            return None
    
    return selected

def audio_capture_thread(sender, device_info, stop_event):
    """Optimized audio capture with device info"""
    if not AUDIO_AVAILABLE or not device_info:
        print("Audio capture disabled (no device)")
        return
    
    p = pyaudio.PyAudio()
    stream = None
    
    try:
        # Audio settings
        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = min(2, device_info['channels'])  # Use stereo if available
        RATE = 44100  # Standard rate
        
        # Try to open stream with preferred settings
        try:
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=device_info['index']
            )
            print(f"Audio capture started: {device_info['name']} ({CHANNELS}ch @ {RATE}Hz)")
        except Exception as e:
            # Try with device's default rate if 44100 fails
            print(f"Failed with 44100Hz, trying {device_info['rate']}Hz...")
            RATE = device_info['rate']
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=device_info['index']
            )
            print(f"Audio capture started: {device_info['name']} ({CHANNELS}ch @ {RATE}Hz)")
        
        # Send initial audio info packet
        info_packet = struct.pack('<4scIIII', b'SYNC', b'I', 12, RATE, CHANNELS, 16)
        sender.send_audio(info_packet)
        
        # Capture loop
        silence_count = 0
        while not stop_event.is_set():
            try:
                audio_data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Check if audio is silent (optional monitoring)
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                is_silent = np.max(np.abs(audio_array)) < 100
                
                if is_silent:
                    silence_count += 1
                    if silence_count == 100:  # Every ~10 seconds of silence
                        print("Audio: Capturing silence (check if source is playing)")
                        silence_count = 0
                else:
                    silence_count = 0
                
                # Create packet
                header = struct.pack('<4scI', b'SYNC', b'A', len(audio_data))
                packet = header + audio_data
                
                # Send via priority queue
                sender.send_audio(packet)
                
            except Exception as e:
                if not stop_event.is_set():
                    print(f"Audio capture error: {e}")
                continue
    
    except Exception as e:
        print(f"Failed to start audio capture: {e}")
        print("Audio will be disabled for this session")
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        p.terminate()

def get_receiver_ip(config):
    """Smart IP input with memory and history"""
    print("\n" + "="*60)
    print("RECEIVER CONNECTION")
    print("="*60)
    
    last_ip = config.get_last_ip()
    history = config.get_ip_history()
    
    # Show connection options
    if last_ip:
        print(f"\n📍 Last connected to: {last_ip}")
        last_connected = config.config.get('last_connected', 'Unknown')
        print(f"   Last connection: {last_connected}")
        print("\nOptions:")
        print(f"  [Enter] - Connect to {last_ip}")
        print(f"  [1]     - Enter new IP address")
        
        if history and len(history) > 1:
            print(f"  [2]     - Show IP history ({len(history)} saved)")
        
        print(f"  [q]     - Quit")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == '' or choice == '\n':
            # Use last IP
            print(f"✓ Connecting to saved IP: {last_ip}")
            return last_ip
        elif choice == '1':
            # Enter new IP
            pass  # Will ask for new IP below
        elif choice == '2' and history and len(history) > 1:
            # Show history
            print("\n" + "-"*40)
            print("IP HISTORY:")
            for i, ip in enumerate(history, 1):
                marker = " ← current" if ip == last_ip else ""
                print(f"  [{i}] {ip}{marker}")
            
            hist_choice = input("\nSelect IP number (or Enter for new): ").strip()
            if hist_choice.isdigit():
                idx = int(hist_choice) - 1
                if 0 <= idx < len(history):
                    selected_ip = history[idx]
                    print(f"✓ Selected: {selected_ip}")
                    return selected_ip
        elif choice == 'q':
            print("Exiting...")
            return None
    
    # Ask for new IP
    print("\nEnter receiver IP address")
    print("Examples: 192.168.1.100, 10.0.0.5")
    
    while True:
        receiver_ip = input("Receiver IP: ").strip()
        
        if not receiver_ip:
            if last_ip:
                print(f"Using last IP: {last_ip}")
                return last_ip
            else:
                print("ERROR: IP address required!")
                continue
        
        # Basic IP validation
        parts = receiver_ip.split('.')
        if len(parts) == 4:
            try:
                if all(0 <= int(part) <= 255 for part in parts):
                    print(f"✓ IP address set: {receiver_ip}")
                    config.add_to_history(receiver_ip)
                    return receiver_ip
            except ValueError:
                pass
        
        print("Invalid IP format! Please use format like: 192.168.1.100")

def get_resolution(config):
    """Get resolution with memory of last selection"""
    last_resolution = config.get_last_resolution()
    
    print("\n" + "="*60)
    print("RESOLUTION SELECTION")
    print("="*60)
    print("\nOptions:")
    print("  720  - HD (1280x720) - Best performance")
    print("  1080 - Full HD (1920x1080) - Balanced")
    print("  1440 - 2K (2560x1440) - High quality")
    print("  4k   - 4K (3840x2160) - Requires fast network")
    
    print(f"\nLast used: {last_resolution}")
    print(f"[Enter] for {last_resolution}, or type new resolution")
    
    choice = input("\nResolution: ").strip().lower()
    
    if not choice:
        return last_resolution
    
    if choice in ['720', '1080', '1440', '4k']:
        return choice
    
    print(f"Invalid choice, using {last_resolution}")
    return last_resolution

def test_connection(ip, port=9999):
    """Quick connection test before streaming"""
    print(f"\nTesting connection to {ip}:{port}...")
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.settimeout(3.0)
    
    try:
        test_sock.connect((ip, port))
        test_sock.close()
        print("✓ Connection test successful!")
        return True
    except socket.timeout:
        print("✗ Connection timeout - Receiver may not be running")
        return False
    except ConnectionRefusedError:
        print("✗ Connection refused - Make sure receiver is running")
        return False
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False

def stream_to_receiver(receiver_ip, resolution, config):
    """Optimized streaming with connection memory"""
    # Parse resolution
    resolutions = {
        '720': (1280, 720),
        '1080': (1920, 1080),
        '1440': (2560, 1440),
        '4k': (3840, 2160)
    }
    width, height = resolutions.get(resolution, (1920, 1080))
    
    print(f"\n=== LAN Screen Sender (Enhanced) ===")
    print(f"Target: {receiver_ip}:9999")
    print(f"Resolution: {width}x{height}")
    print(f"Audio: {'Available' if AUDIO_AVAILABLE else 'Disabled (PyAudio not installed)'}")
    
    # Quick connection test
    if not test_connection(receiver_ip):
        retry = input("\nRetry connection? (y/n): ").strip().lower()
        if retry != 'y':
            return False
        if not test_connection(receiver_ip):
            print("Still cannot connect. Please check:")
            print("  1. Receiver is running")
            print("  2. IP address is correct")
            print("  3. Firewall is not blocking port 9999")
            return False
    
    # Save successful connection details
    config.update_connection(receiver_ip, resolution)
    
    # Select audio device
    audio_device = None
    if AUDIO_AVAILABLE:
        audio_device = select_audio_device()
        if not audio_device:
            print("Continuing without audio...")
    
    # Initialize screen capture
    print("\nInitializing screen capture...")
    camera = dxcam.create(output_idx=0, output_color="BGR")
    if not camera:
        print("ERROR: Failed to initialize screen capture!")
        return False
    
    # Start capture
    camera.start(target_fps=60, video_mode=True)
    
    # Connect to receiver
    print(f"Connecting to {receiver_ip}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
    
    try:
        sock.settimeout(5.0)
        sock.connect((receiver_ip, 9999))
        sock.settimeout(None)
        print("Connected! Starting stream...\n")
        
        # Create dual-queue sender
        sender = DualNetworkSender(sock)
        
        # Start audio thread
        stop_event = threading.Event()
        audio_thread = None
        if audio_device:
            audio_thread = threading.Thread(
                target=audio_capture_thread,
                args=(sender, audio_device, stop_event)
            )
            audio_thread.start()
        
        # Video settings
        frame_count = 0
        fps_timer = time.time()
        fps_counter = 0
        stats_timer = time.time()
        
        # Adaptive quality
        quality = 85
        min_quality = 60
        max_quality = 95
        target_fps = 60
        frame_time = 1.0 / target_fps
        last_frame_time = time.time()
        
        # Main loop
        print("Streaming... Press Ctrl+C to stop\n")
        while True:
            current_time = time.time()
            
            # Frame pacing
            if current_time - last_frame_time < frame_time:
                time.sleep(0.001)
                continue
            
            # Capture frame
            frame = camera.get_latest_frame()
            if frame is None:
                continue
            
            last_frame_time = current_time
            
            # Resize if needed
            if frame.shape[:2] != (height, width):
                frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
            
            # Encode frame
            encode_param = [
                int(cv2.IMWRITE_JPEG_QUALITY), quality,
                int(cv2.IMWRITE_JPEG_OPTIMIZE), 0,
                int(cv2.IMWRITE_JPEG_PROGRESSIVE), 0
            ]
            result, encoded = cv2.imencode('.jpg', frame, encode_param)
            
            if not result:
                continue
            
            # Create packet
            data = encoded.tobytes()
            header = struct.pack('<4scI', b'SYNC', b'V', len(data))
            packet = header + data
            
            # Send via video queue
            if sender.send_video(packet):
                frame_count += 1
                fps_counter += 1
            
            # Update FPS and stats
            if current_time - fps_timer >= 1.0:
                fps = fps_counter
                fps_counter = 0
                fps_timer = current_time
                
                # Adjust quality based on dropped frames
                stats = sender.get_stats()
                if stats['video_dropped'] > 5 and quality > min_quality:
                    quality -= 5
                elif stats['video_dropped'] == 0 and quality < max_quality:
                    quality += 2
                
                # Display stats
                audio_status = "ON" if audio_device else "OFF"
                print(f"\rFPS: {fps:3d} | Quality: {quality}% | Frames: {frame_count:6d} | "
                      f"Audio: {audio_status} | Sent: V:{stats['video_sent']} A:{stats['audio_sent']} | "
                      f"Dropped: V:{stats['video_dropped']} A:{stats['audio_dropped']}", end='')
                
    except ConnectionRefusedError:
        print(f"ERROR: Cannot connect to {receiver_ip}:9999")
        print("Make sure receiver is running!")
        return False
    except KeyboardInterrupt:
        print("\n\nStopping stream...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        stop_event.set()
        sender.stop()
        if audio_thread:
            audio_thread.join(timeout=1)
        camera.stop()
        sock.close()
        print("\nStream ended.")
    
    return True

def setup_receiver_ip(settings):
    """Setup or change receiver IP"""
    print("\n" + "="*60)
    print("                RECEIVER IP SETUP")
    print("="*60)
    
    current_ip = settings.settings.get('receiver_ip')
    if current_ip and not settings.is_first_run():
        print(f"\nCurrent IP: {current_ip}")
        print("Press Enter to keep current IP, or enter a new one")
    else:
        print("\nEnter the IP address of the receiver PC")
        print("(The PC that will display the stream)")
    
    print("\nExample: 192.168.1.100")
    while True:
        new_ip = input("Receiver IP: ").strip()
        if not new_ip:
            if current_ip:
                print(f"Keeping current IP: {current_ip}")
                return current_ip
            print("IP address is required!")
            continue
        
        # Validate IP
        parts = new_ip.split('.')
        if len(parts) == 4:
            try:
                if all(0 <= int(part) <= 255 for part in parts):
                    settings.update_connection(ip=new_ip)
                    print(f"✓ IP address updated: {new_ip}")
                    return new_ip
            except ValueError:
                pass
        print("Invalid IP format!")

def setup_audio_device(settings):
    """Setup or change audio device"""
    print("\n" + "="*60)
    print("               AUDIO DEVICE SETUP")
    print("="*60)
    
    if not AUDIO_AVAILABLE:
        print("\nAudio not available (PyAudio not installed)")
        return None
    
    devices = enumerate_audio_devices()
    if not devices:
        print("\nNo audio devices found!")
        return None
    
    print("\nSelect audio device:")
    print("[0] Disable audio")
    
    choice = input("\nDevice number: ").strip()
    
    if choice == '0':
        settings.update_connection(audio_device=-1, audio_name='Disabled')
        print("Audio disabled")
        return None
    
    try:
        idx = int(choice)
        for device in devices:
            if device['index'] == idx:
                settings.update_connection(
                    audio_device=device['index'],
                    audio_name=device['name']
                )
                print(f"✓ Selected: {device['name']}")
                return device
    except:
        pass
    
    print("Invalid selection")
    return None

def setup_resolution(settings):
    """Setup or change resolution"""
    print("\n" + "="*60)
    print("              RESOLUTION SETUP")
    print("="*60)
    
    print("\nSelect resolution:")
    print("  [1] 720p  (1280x720)  - Best performance")
    print("  [2] 1080p (1920x1080) - Balanced")
    print("  [3] 1440p (2560x1440) - High quality")
    print("  [4] 4K    (3840x2160) - Ultra quality")
    
    current = settings.settings.get('resolution', '1080')
    print(f"\nCurrent: {current.upper()}")
    
    choice = input("Select [1-4]: ").strip()
    
    res_map = {'1': '720', '2': '1080', '3': '1440', '4': '4k'}
    if choice in res_map:
        resolution = res_map[choice]
        settings.update_connection(resolution=resolution)
        print(f"✓ Resolution set to {resolution.upper()}")
        return resolution
    
    print(f"Invalid choice, keeping {current}")
    return current

def setup_quality(settings):
    """Setup or change quality preset"""
    print("\n" + "="*60)
    print("               QUALITY SETUP")
    print("="*60)
    
    print("\nSelect quality preset:")
    print("  [1] Low      - Fast, lower quality")
    print("  [2] Balanced - Good balance")
    print("  [3] High     - Better quality")
    print("  [4] Ultra    - Best quality")
    
    current = settings.settings.get('quality', 'balanced')
    print(f"\nCurrent: {current.capitalize()}")
    
    choice = input("Select [1-4]: ").strip()
    
    quality_map = {'1': 'low', '2': 'balanced', '3': 'high', '4': 'ultra'}
    if choice in quality_map:
        quality = quality_map[choice]
        settings.update_connection(quality=quality)
        print(f"✓ Quality set to {quality.capitalize()}")
        return quality
    
    print(f"Invalid choice, keeping {current}")
    return current

def full_setup(settings):
    """Run complete setup wizard"""
    print("\n" + "="*60)
    print("           STREAMING SETUP WIZARD")
    print("="*60)
    print("\nLet's configure your streaming settings...\n")
    
    # Setup each component
    setup_receiver_ip(settings)
    setup_audio_device(settings)
    setup_resolution(settings)
    setup_quality(settings)
    
    # Mark setup complete
    settings.mark_setup_complete()
    
    print("\n" + "="*60)
    print("✓ Setup complete! Your settings have been saved.")
    print("="*60)

def quick_connect(settings):
    """Connect with saved settings"""
    last = settings.get_last_connection()
    
    if not last['ip']:
        print("\nNo saved connection found. Running setup...")
        full_setup(settings)
        last = settings.get_last_connection()
    
    print("\nConnecting with saved settings...")
    settings.display_current_settings()
    
    # Get audio device info if configured
    audio_device = None
    if AUDIO_AVAILABLE and settings.get_audio_device() is not None:
        if settings.get_audio_device() >= 0:
            # Find the device info
            devices = enumerate_audio_devices()
            for device in devices:
                if device['index'] == settings.get_audio_device():
                    audio_device = device
                    break
    
    # Get quality settings
    quality_settings = settings.get_quality_settings()
    
    # Start streaming with saved settings
    stream_with_settings(
        settings.settings['receiver_ip'],
        settings.settings['resolution'],
        audio_device,
        quality_settings,
        settings
    )

def stream_with_settings(receiver_ip, resolution, audio_device, quality_settings, settings):
    """Stream with specific settings"""
    # Get resolution dimensions
    width, height = settings.get_resolution_preset(resolution)
    if width is None:  # Auto resolution
        width, height = 1920, 1080  # Default
    
    print(f"\n=== Starting Stream ===")
    print(f"Receiver: {receiver_ip}:9999")
    print(f"Resolution: {width}x{height}")
    print(f"Quality: {quality_settings}")
    print(f"Audio: {audio_device['name'] if audio_device else 'Disabled'}")
    
    # Test connection
    if not test_connection(receiver_ip):
        print("\nConnection failed! Please check:")
        print("  1. Receiver is running")
        print("  2. IP address is correct")
        print("  3. Firewall allows port 9999")
        return False
    
    # Initialize capture
    print("\nInitializing screen capture...")
    camera = dxcam.create(output_idx=0, output_color="BGR")
    if not camera:
        print("ERROR: Failed to initialize screen capture!")
        return False
    
    camera.start(target_fps=quality_settings['fps'], video_mode=True)
    
    # Connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
    
    try:
        sock.connect((receiver_ip, 9999))
        print("Connected! Streaming...\n")
        print("Press Ctrl+C to stop\n")
        
        # Create sender
        sender = DualNetworkSender(sock)
        
        # Start audio if configured
        stop_event = threading.Event()
        audio_thread = None
        if audio_device:
            audio_thread = threading.Thread(
                target=audio_capture_thread,
                args=(sender, audio_device, stop_event)
            )
            audio_thread.start()
        
        # Streaming loop
        frame_count = 0
        fps_timer = time.time()
        fps_counter = 0
        quality = quality_settings['jpeg_quality']
        
        while True:
            frame = camera.get_latest_frame()
            if frame is None:
                continue
            
            # Resize if needed
            if frame.shape[:2] != (height, width):
                frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
            
            # Encode
            encode_param = [
                int(cv2.IMWRITE_JPEG_QUALITY), quality,
                int(cv2.IMWRITE_JPEG_OPTIMIZE), 0
            ]
            result, encoded = cv2.imencode('.jpg', frame, encode_param)
            
            if result:
                data = encoded.tobytes()
                header = struct.pack('<4scI', b'SYNC', b'V', len(data))
                if sender.send_video(header + data):
                    frame_count += 1
                    fps_counter += 1
            
            # Update FPS
            if time.time() - fps_timer >= 1.0:
                fps = fps_counter
                fps_counter = 0
                fps_timer = time.time()
                
                stats = sender.get_stats()
                print(f"\rFPS: {fps:3d} | Frames: {frame_count:6d} | "
                      f"Sent: V:{stats['video_sent']} A:{stats['audio_sent']}", end='')
                
    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        stop_event.set()
        sender.stop()
        if audio_thread:
            audio_thread.join(timeout=1)
        camera.stop()
        sock.close()
        
        # Update last connected time
        settings.settings['last_connected'] = time.strftime("%Y-%m-%d %H:%M:%S")
        settings.save_settings()
        
        print("\nStream ended.")
    
    return True

def main():
    """Main entry point with CLI argument support"""
    parser = argparse.ArgumentParser(description='LAN Screen Sender')
    parser.add_argument('--quick', action='store_true', help='Quick connect with saved settings')
    parser.add_argument('--first-run', action='store_true', help='Run first-time setup')
    parser.add_argument('--full-setup', action='store_true', help='Run complete setup')
    parser.add_argument('--change-ip', action='store_true', help='Change receiver IP only')
    parser.add_argument('--change-audio', action='store_true', help='Change audio device only')
    parser.add_argument('--change-resolution', action='store_true', help='Change resolution only')
    parser.add_argument('--change-quality', action='store_true', help='Change quality only')
    
    args = parser.parse_args()
    
    # Initialize settings
    settings = get_settings()
    
    print("\n" + "="*60)
    print("         LAN SCREEN SENDER v1.0")
    print("="*60)
    
    try:
        if args.first_run or (settings.is_first_run() and not args.quick):
            # First time setup
            full_setup(settings)
            # After setup, start streaming
            quick_connect(settings)
            
        elif args.full_setup:
            # Full reconfiguration
            full_setup(settings)
            quick_connect(settings)
            
        elif args.change_ip:
            # Change IP only
            setup_receiver_ip(settings)
            quick_connect(settings)
            
        elif args.change_audio:
            # Change audio only
            setup_audio_device(settings)
            quick_connect(settings)
            
        elif args.change_resolution:
            # Change resolution only
            setup_resolution(settings)
            quick_connect(settings)
            
        elif args.change_quality:
            # Change quality only
            setup_quality(settings)
            quick_connect(settings)
            
        elif args.quick:
            # Quick connect
            quick_connect(settings)
            
        else:
            # Default: interactive mode
            if settings.is_first_run():
                full_setup(settings)
            quick_connect(settings)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
