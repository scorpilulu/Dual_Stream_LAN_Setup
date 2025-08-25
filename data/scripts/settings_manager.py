"""
Settings Manager - Centralized configuration management for LAN Streamer
Handles persistent storage of user preferences with intuitive defaults
"""
import json
import os
import time
from pathlib import Path

class SettingsManager:
    """Manages all application settings with persistence"""
    
    def __init__(self):
        # Get the config directory path
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config_file = self.config_dir / "stream_config.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default settings
        self.defaults = {
            'receiver_ip': None,
            'audio_device': None,
            'audio_device_name': 'System Default',
            'resolution': '1080',
            'quality': 'balanced',
            'fps': 30,
            'first_run': True,
            'last_connected': None,
            'ip_history': [],
            'quick_settings': {
                'use_last': True
            }
        }
        
        # Resolution presets
        self.resolution_presets = {
            '720': (1280, 720),
            '1080': (1920, 1080),
            '1440': (2560, 1440),
            '4k': (3840, 2160),
            'auto': None  # Will use native resolution
        }
        
        # Quality presets
        self.quality_presets = {
            'low': {'jpeg_quality': 60, 'fps': 20},
            'balanced': {'jpeg_quality': 75, 'fps': 30},
            'high': {'jpeg_quality': 85, 'fps': 30},
            'ultra': {'jpeg_quality': 95, 'fps': 60}
        }
        
        # Load existing settings
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file or create with defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.defaults.copy()
                    settings.update(loaded)
                    return settings
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.defaults.copy()
        return self.defaults.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def is_first_run(self):
        """Check if this is the first time running"""
        return self.settings.get('first_run', True)
    
    def mark_setup_complete(self):
        """Mark that initial setup has been completed"""
        self.settings['first_run'] = False
        self.save_settings()
    
    def get_last_connection(self):
        """Get last connection details"""
        return {
            'ip': self.settings.get('receiver_ip'),
            'audio': self.settings.get('audio_device_name', 'System Default'),
            'resolution': self.settings.get('resolution', '1080'),
            'quality': self.settings.get('quality', 'balanced'),
            'timestamp': self.settings.get('last_connected')
        }
    
    def update_connection(self, ip=None, audio_device=None, audio_name=None, 
                         resolution=None, quality=None):
        """Update connection settings"""
        if ip:
            self.settings['receiver_ip'] = ip
            self.add_to_history(ip)
        if audio_device is not None:
            self.settings['audio_device'] = audio_device
        if audio_name:
            self.settings['audio_device_name'] = audio_name
        if resolution:
            self.settings['resolution'] = resolution
        if quality:
            self.settings['quality'] = quality
        
        self.settings['last_connected'] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.save_settings()
    
    def add_to_history(self, ip):
        """Add IP to connection history"""
        history = self.settings.get('ip_history', [])
        if ip not in history:
            history.append(ip)
            # Keep only last 5 unique IPs
            if len(history) > 5:
                history = history[-5:]
            self.settings['ip_history'] = history
    
    def get_ip_history(self):
        """Get list of previously used IPs"""
        return self.settings.get('ip_history', [])
    
    def get_resolution_preset(self, key=None):
        """Get resolution dimensions for a preset"""
        if key is None:
            key = self.settings.get('resolution', '1080')
        return self.resolution_presets.get(key, self.resolution_presets['1080'])
    
    def get_quality_settings(self, key=None):
        """Get quality settings for a preset"""
        if key is None:
            key = self.settings.get('quality', 'balanced')
        return self.quality_presets.get(key, self.quality_presets['balanced'])
    
    def get_audio_device(self):
        """Get selected audio device index"""
        return self.settings.get('audio_device', None)
    
    def clear_settings(self):
        """Reset all settings to defaults"""
        self.settings = self.defaults.copy()
        self.save_settings()
    
    def display_current_settings(self):
        """Display current settings in a formatted way"""
        print("\n" + "="*60)
        print("              CURRENT SETTINGS")
        print("="*60)
        
        last = self.get_last_connection()
        
        if last['ip']:
            print(f"  Receiver IP:     {last['ip']}")
        else:
            print(f"  Receiver IP:     Not configured")
        
        print(f"  Audio Device:    {last['audio']}")
        print(f"  Resolution:      {last['resolution'].upper()}")
        print(f"  Quality:         {last['quality'].capitalize()}")
        
        if last['timestamp']:
            print(f"  Last Connected:  {last['timestamp']}")
        
        print("="*60)
        
        return last

# Singleton instance
_settings_instance = None

def get_settings():
    """Get or create the singleton settings instance"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance
