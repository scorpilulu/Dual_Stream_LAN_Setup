"""
LAN Screen Receiver - Enhanced Audio Selection Edition
Allows manual selection of audio output device
"""
import sys
import socket
import struct
import time
import cv2
import numpy as np
import threading
import queue
import collections
import json
import os

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    print("WARNING: PyAudio not installed! Audio playback disabled.")
    print("To enable audio, run: pip install pyaudio")
    AUDIO_AVAILABLE = False
    pyaudio = None

class NetworkReceiver:
    """Optimized network receiver with buffering"""
    def __init__(self, sock):
        self.sock = sock
        self.buffer = b''
        
    def receive_exact(self, num_bytes):
        """Receive exactly num_bytes with buffering"""
        while len(self.buffer) < num_bytes:
            chunk = self.sock.recv(65536)  # Receive larger chunks
            if not chunk:
                return None
            self.buffer += chunk
        
        data = self.buffer[:num_bytes]
        self.buffer = self.buffer[num_bytes:]
        return data

def enumerate_audio_outputs():
    """List all audio output devices"""
    if not AUDIO_AVAILABLE:
        return []
    
    p = pyaudio.PyAudio()
    devices = []
    
    try:
        print("\n=== Available Audio Output Devices ===")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxOutputChannels'],
                    'rate': int(info['defaultSampleRate']),
                    'is_default': i == p.get_default_output_device_info()['index']
                })
                status = " [DEFAULT]" if devices[-1]['is_default'] else ""
                print(f"  [{i}] {info['name']} ({info['maxOutputChannels']}ch @ {int(info['defaultSampleRate'])}Hz){status}")
    except Exception as e:
        print(f"Error listing output devices: {e}")
    finally:
        p.terminate()
    
    return devices

def select_audio_output_device():
    """Let user select audio output device or use saved preference"""
    if not AUDIO_AVAILABLE:
        return None
    
    devices = enumerate_audio_outputs()
    if not devices:
        print("ERROR: No audio output devices found!")
        return None
    
    # Check for saved preference
    config_file = "audio_output_config.json"
    saved_device = None
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                saved_index = config.get('output_device_index')
                if saved_index is not None:
                    for device in devices:
                        if device['index'] == saved_index:
                            saved_device = device
                            print(f"\n✓ Using saved preference: {device['name']}")
                            break
        except:
            pass
    
    # If we have a saved device, ask if user wants to keep it
    if saved_device:
        print("\nPress Enter to keep this device, or type a new device number: ")
        choice = input().strip()
        
        if not choice:  # User pressed Enter, keep saved device
            return saved_device
        else:
            try:
                idx = int(choice)
                for device in devices:
                    if device['index'] == idx:
                        # Save new preference
                        with open(config_file, 'w') as f:
                            json.dump({'output_device_index': idx}, f)
                        print(f"✓ Selected and saved: {device['name']}")
                        return device
            except:
                print("Invalid selection, using saved device")
                return saved_device
    
    # No saved preference, ask user to choose
    print("\n" + "="*50)
    print("AUDIO OUTPUT SELECTION")
    print("="*50)
    
    # Find default device as fallback
    default_device = None
    for device in devices:
        if device['is_default']:
            default_device = device
            break
    
    if not default_device:
        default_device = devices[0]  # Use first available if no default
    
    print(f"\nDefault device: {default_device['name']}")
    print("\nOptions:")
    print("  - Press Enter to use default device")
    print("  - Enter device number from list above")
    print("  - Type 'none' to disable audio")
    
    choice = input("\nYour choice: ").strip().lower()
    
    if choice == 'none':
        print("Audio playback disabled by user choice")
        return None
    elif not choice:  # Enter pressed, use default
        selected = default_device
        print(f"✓ Using default: {selected['name']}")
    else:
        try:
            idx = int(choice)
            selected = None
            for device in devices:
                if device['index'] == idx:
                    selected = device
                    print(f"✓ Selected: {device['name']}")
                    break
            
            if not selected:
                print(f"Device {idx} not found, using default")
                selected = default_device
        except:
            print("Invalid input, using default device")
            selected = default_device
    
    # Save preference
    try:
        with open(config_file, 'w') as f:
            json.dump({'output_device_index': selected['index']}, f)
        print(f"Preference saved for next time")
    except:
        pass
    
    return selected

def audio_playback_thread(audio_queue, stop_event, audio_info_queue, output_device):
    """Enhanced audio playback with user-selected device"""
    if not AUDIO_AVAILABLE or not output_device:
        print("Audio playback disabled")
        return
    
    p = pyaudio.PyAudio()
    stream = None
    
    # Default audio settings (will be updated from sender)
    CHUNK = 4096
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    
    print(f"\n✓ Audio output initialized: {output_device['name']}")
    
    # Audio buffer for smooth playback
    audio_buffer = collections.deque(maxlen=20)
    stream_configured = False
    
    while not stop_event.is_set():
        try:
            # Check for audio configuration updates
            try:
                audio_info = audio_info_queue.get_nowait()
                new_rate = audio_info.get('rate', RATE)
                new_channels = audio_info.get('channels', CHANNELS)
                
                if new_rate != RATE or new_channels != CHANNELS or not stream_configured:
                    # Reconfigure stream with new settings
                    if stream:
                        stream.stop_stream()
                        stream.close()
                    
                    RATE = new_rate
                    CHANNELS = new_channels
                    
                    # Try multiple configurations
                    configs_to_try = [
                        (RATE, CHANNELS),  # Try exact configuration
                        (44100, CHANNELS),  # Try standard rate
                        (48000, CHANNELS),  # Try 48kHz
                        (RATE, 2),  # Try stereo at original rate
                        (44100, 2),  # Try standard stereo
                        (48000, 2),  # Try 48kHz stereo
                    ]
                    
                    for test_rate, test_channels in configs_to_try:
                        try:
                            stream = p.open(
                                format=FORMAT,
                                channels=test_channels,
                                rate=test_rate,
                                output=True,
                                frames_per_buffer=CHUNK,
                                output_device_index=output_device['index']
                            )
                            RATE = test_rate
                            CHANNELS = test_channels
                            print(f"Audio playback configured: {CHANNELS}ch @ {RATE}Hz on {output_device['name']}")
                            stream_configured = True
                            break
                        except Exception as e:
                            continue
                    
                    if not stream_configured:
                        print(f"ERROR: Could not configure audio output on {output_device['name']}!")
                        print(f"Tried rates: {[c[0] for c in configs_to_try]}")
                        p.terminate()
                        return
                        
            except queue.Empty:
                pass
            
            # Initialize stream if not done yet
            if not stream_configured:
                try:
                    stream = p.open(
                        format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK,
                        output_device_index=output_device['index']
                    )
                    print(f"Audio playback started: {CHANNELS}ch @ {RATE}Hz on {output_device['name']}")
                    stream_configured = True
                except Exception as e:
                    print(f"Failed to initialize audio on {output_device['name']}: {e}")
                    time.sleep(1)
                    continue
            
            # Try to maintain buffer
            while not audio_queue.empty() and len(audio_buffer) < 10:
                try:
                    audio_buffer.append(audio_queue.get_nowait())
                except queue.Empty:
                    break
            
            # Play from buffer
            if audio_buffer and stream:
                try:
                    audio_data = audio_buffer.popleft()
                    stream.write(audio_data, exception_on_underflow=False)
                except Exception as e:
                    if not stop_event.is_set():
                        print(f"Audio playback error: {e}")
            else:
                # Wait for more data
                time.sleep(0.005)
                
        except Exception as e:
            if not stop_event.is_set():
                print(f"Audio thread error: {e}")
            time.sleep(0.1)
    
    # Cleanup
    if stream:
        stream.stop_stream()
        stream.close()
    p.terminate()
    print("Audio playback stopped")

def frame_display_thread(frame_queue, stop_event):
    """Separate thread for displaying frames smoothly"""
    window_name = "LAN Stream HD"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    frame_count = 0
    fps_timer = time.time()
    fps_counter = 0
    is_fullscreen = False
    
    # Frame timing for smooth playback
    target_fps = 60
    frame_time = 1.0 / target_fps
    last_display_time = time.time()
    
    while not stop_event.is_set():
        try:
            # Get frame with timeout
            frame = frame_queue.get(timeout=0.1)
            
            # Frame pacing for smooth display
            current_time = time.time()
            elapsed = current_time - last_display_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)
            
            # Display frame
            cv2.imshow(window_name, frame)
            last_display_time = time.time()
            
            frame_count += 1
            fps_counter += 1
            
            # Calculate FPS
            if current_time - fps_timer >= 1.0:
                fps = fps_counter
                fps_counter = 0
                fps_timer = current_time
                print(f"\rFPS: {fps:3d} | Frames: {frame_count:6d} | Audio: {'ON' if AUDIO_AVAILABLE else 'OFF'}", end='')
            
            # Check for keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # Q or ESC
                stop_event.set()
                break
            elif key == ord('f'):  # F for fullscreen
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            elif key == ord('a'):  # A to show audio status
                print(f"\nAudio Status: {'Enabled' if AUDIO_AVAILABLE else 'Disabled (PyAudio not installed)'}")
                    
        except queue.Empty:
            continue
        except Exception as e:
            if not stop_event.is_set():
                print(f"\nDisplay error: {e}")
    
    cv2.destroyWindow(window_name)

def main():
    print("=== LAN Screen Receiver (Enhanced Audio Selection) ===")
    print(f"Audio Support: {'Enabled' if AUDIO_AVAILABLE else 'Disabled (install PyAudio to enable)'}")
    
    # Let user select audio output device BEFORE starting the server
    output_device = None
    if AUDIO_AVAILABLE:
        output_device = select_audio_output_device()
        if not output_device:
            print("\nContinuing without audio output...")
        print()
    
    print("Listening on port 9999...")
    print()
    
    # Create server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    server_sock.bind(('0.0.0.0', 9999))
    server_sock.listen(1)
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Your IP address: {local_ip}")
    print("Waiting for sender...")
    print()
    
    while True:
        try:
            # Accept connection
            client_sock, addr = server_sock.accept()
            
            # Optimize socket settings
            client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)  # 1MB buffer
            
            print(f"Connected to: {addr[0]}:{addr[1]}")
            print("Starting stream...")
            print("\nControls:")
            print("  Q/ESC - Quit")
            print("  F - Toggle fullscreen")
            print("  A - Show audio status")
            print()
            
            # Create queues with proper sizes
            stop_event = threading.Event()
            frame_queue = queue.Queue(maxsize=5)  # Small buffer for low latency
            audio_queue = queue.Queue(maxsize=30)  # Larger for audio buffering
            audio_info_queue = queue.Queue(maxsize=1)  # For audio configuration
            
            # Start display thread
            display_thread = threading.Thread(
                target=frame_display_thread,
                args=(frame_queue, stop_event)
            )
            display_thread.start()
            
            # Start audio thread with selected device
            audio_thread = threading.Thread(
                target=audio_playback_thread,
                args=(audio_queue, stop_event, audio_info_queue, output_device)
            )
            audio_thread.start()
            
            # Network receiver
            receiver = NetworkReceiver(client_sock)
            
            # Statistics
            stats = {
                'video_received': 0,
                'audio_received': 0,
                'sync_errors': 0,
                'packets_dropped': 0
            }
            
            # Receiving loop
            consecutive_errors = 0
            last_stats_time = time.time()
            
            while not stop_event.is_set():
                try:
                    # Receive header
                    header = receiver.receive_exact(9)
                    if not header:
                        print("\nConnection closed by sender")
                        break
                    
                    # Parse header
                    try:
                        sync, data_type, data_size = struct.unpack('<4scI', header)
                    except struct.error:
                        stats['sync_errors'] += 1
                        consecutive_errors += 1
                        if consecutive_errors > 10:
                            print("\nToo many sync errors, disconnecting")
                            break
                        continue
                    
                    # Validate sync
                    if sync != b'SYNC':
                        stats['sync_errors'] += 1
                        print(f"\nSync error: expected SYNC, got {sync}")
                        continue
                    
                    consecutive_errors = 0
                    
                    # Validate size
                    if data_size > 10 * 1024 * 1024:  # Max 10MB
                        stats['packets_dropped'] += 1
                        print(f"\nInvalid packet size: {data_size}")
                        continue
                    
                    # Receive data
                    data = receiver.receive_exact(data_size)
                    if not data:
                        print("\nConnection lost while receiving data")
                        break
                    
                    # Handle based on type
                    if data_type == b'V':  # Video frame
                        stats['video_received'] += 1
                        try:
                            # Decode JPEG
                            nparr = np.frombuffer(data, np.uint8)
                            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            
                            if frame is not None:
                                # Add to frame queue (drop if full for low latency)
                                if not frame_queue.full():
                                    frame_queue.put_nowait(frame)
                                else:
                                    stats['packets_dropped'] += 1
                        except Exception as e:
                            print(f"\nFrame decode error: {e}")
                    
                    elif data_type == b'A':  # Audio chunk
                        stats['audio_received'] += 1
                        try:
                            if not audio_queue.full():
                                audio_queue.put_nowait(data)
                            else:
                                # Drop oldest audio to make room
                                try:
                                    audio_queue.get_nowait()
                                    audio_queue.put_nowait(data)
                                    stats['packets_dropped'] += 1
                                except:
                                    pass
                        except:
                            pass
                    
                    elif data_type == b'I':  # Audio info packet
                        try:
                            rate, channels, bits = struct.unpack('<III', data)
                            audio_info = {'rate': rate, 'channels': channels, 'bits': bits}
                            # Clear old info and add new
                            while not audio_info_queue.empty():
                                audio_info_queue.get_nowait()
                            audio_info_queue.put_nowait(audio_info)
                            print(f"\nAudio format update: {channels}ch @ {rate}Hz, {bits}-bit")
                        except:
                            pass
                    
                    # Print statistics periodically
                    current_time = time.time()
                    if current_time - last_stats_time >= 10.0:
                        print(f"\n[Stats] Video: {stats['video_received']} | Audio: {stats['audio_received']} | "
                              f"Dropped: {stats['packets_dropped']} | Sync Errors: {stats['sync_errors']}")
                        last_stats_time = current_time
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    if not stop_event.is_set():
                        print(f"\nReceive error: {e}")
                    consecutive_errors += 1
                    if consecutive_errors > 10:
                        break
            
            # Cleanup
            stop_event.set()
            display_thread.join(timeout=2)
            audio_thread.join(timeout=2)
            client_sock.close()
            
            print("\n\nConnection closed. Waiting for new sender...")
            print()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    server_sock.close()
    cv2.destroyAllWindows()
    print("\nReceiver stopped.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nReceiver stopped by user.")
        cv2.destroyAllWindows()
