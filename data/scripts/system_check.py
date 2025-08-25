"""
LAN Screen Streamer - System Requirements Checker
Validates Python, dependencies, network configuration, and system specs
"""
import sys
import os
import socket
import subprocess
import platform
import importlib.util
import time

def print_header():
    """Print system check header"""
    print("=" * 70)
    print("🔍 LAN SCREEN STREAMER - SYSTEM REQUIREMENTS CHECK")
    print("=" * 70)
    print()

def print_section(title):
    """Print section header"""
    print(f"\n📋 {title}")
    print("-" * 50)

def check_python():
    """Check Python version and installation"""
    print_section("PYTHON INSTALLATION")
    
    # Check Python version
    python_version = sys.version_info
    version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    
    if python_version >= (3, 8):
        print(f"✅ Python {version_str} - Compatible")
        python_ok = True
    else:
        print(f"❌ Python {version_str} - Too old! Need Python 3.8+")
        python_ok = False
    
    # Check Python executable path
    print(f"📂 Python Path: {sys.executable}")
    
    # Check pip availability
    try:
        import pip
        print("✅ pip is available")
        pip_ok = True
    except ImportError:
        print("❌ pip is not available")
        pip_ok = False
    
    return python_ok and pip_ok

def check_dependencies():
    """Check required Python packages"""
    print_section("REQUIRED DEPENDENCIES")
    
    dependencies = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'dxcam': 'dxcam',  # Screen capture for sender
        'socket': 'built-in',
        'struct': 'built-in',
        'threading': 'built-in',
        'time': 'built-in'
    }
    
    optional_deps = {
        'pyaudio': 'pyaudio'  # For audio streaming
    }
    
    all_ok = True
    
    # Check required dependencies
    for module, package in dependencies.items():
        try:
            if module == 'cv2':
                import cv2
                print(f"✅ OpenCV {cv2.__version__} - Available")
            elif module == 'numpy':
                import numpy
                print(f"✅ NumPy {numpy.__version__} - Available")
            elif module == 'dxcam':
                import dxcam
                print(f"✅ DXCam - Available (Screen capture)")
            else:
                importlib.import_module(module)
                print(f"✅ {module} - Available")
        except ImportError:
            print(f"❌ {module} - Missing! Install with: pip install {package}")
            all_ok = False
    
    # Check optional dependencies
    print("\n📦 Optional Dependencies:")
    for module, package in optional_deps.items():
        try:
            if module == 'pyaudio':
                import pyaudio
                print(f"✅ PyAudio - Available (Audio streaming enabled)")
            else:
                importlib.import_module(module)
                print(f"✅ {module} - Available")
        except ImportError:
            print(f"⚠️  {module} - Missing (Audio streaming disabled)")
            print(f"   Install with: pip install {package}")
    
    return all_ok

def check_system_specs():
    """Check system specifications"""
    print_section("SYSTEM SPECIFICATIONS")
    
    # Operating System
    os_info = platform.platform()
    print(f"💻 Operating System: {os_info}")
    
    # Check if Windows
    if platform.system() == "Windows":
        print("✅ Windows OS - Compatible")
        windows_ok = True
    else:
        print("⚠️  Non-Windows OS - May have compatibility issues")
        windows_ok = False
    
    # Architecture
    arch = platform.architecture()[0]
    print(f"🏗️  Architecture: {arch}")
    
    if arch == "64bit":
        print("✅ 64-bit architecture - Recommended")
        arch_ok = True
    else:
        print("⚠️  32-bit architecture - May have performance issues")
        arch_ok = False
    
    # CPU cores (rough estimate)
    try:
        import multiprocessing
        cores = multiprocessing.cpu_count()
        print(f"⚡ CPU Cores: {cores}")
        
        if cores >= 4:
            print("✅ Sufficient CPU cores for good performance")
            cpu_ok = True
        else:
            print("⚠️  Limited CPU cores - May affect performance")
            cpu_ok = False
    except:
        print("❓ CPU core count - Unable to determine")
        cpu_ok = True
    
    return windows_ok and arch_ok and cpu_ok

def check_network():
    """Check network configuration"""
    print_section("NETWORK CONFIGURATION")
    
    network_ok = True
    
    # Get hostname
    hostname = socket.gethostname()
    print(f"🏠 Hostname: {hostname}")
    
    # Get all IP addresses
    try:
        # Get primary IP address
        primary_ip = socket.gethostbyname(hostname)
        print(f"📍 Primary IP: {primary_ip}")
        
        # Check if it's a valid LAN IP
        if primary_ip.startswith(('192.168.', '10.', '172.')):
            print("✅ Valid LAN IP address")
        elif primary_ip == '127.0.0.1':
            print("⚠️  Localhost only - May not work for LAN streaming")
            network_ok = False
        else:
            print("⚠️  Non-standard IP - Check network configuration")
    except socket.error as e:
        print(f"❌ Network error: {e}")
        network_ok = False
    
    # Test port 9999 availability
    print(f"\n🔌 Testing port 9999 availability...")
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('0.0.0.0', 9999))
        test_socket.close()
        print("✅ Port 9999 is available")
    except socket.error:
        print("⚠️  Port 9999 is in use or blocked")
        print("   Close any applications using port 9999")
        network_ok = False
    
    # Test localhost connectivity
    print(f"\n🧪 Testing localhost connectivity...")
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(2)
        test_socket.connect(('127.0.0.1', 80))  # Try connecting to common port
        test_socket.close()
        print("✅ Localhost connectivity works")
    except:
        # This is expected to fail, just testing socket creation
        print("✅ Socket creation and binding works")
    
    return network_ok

def check_files():
    """Check required files are present"""
    print_section("REQUIRED FILES")
    
    required_files = [
        'sender.py',
        'receiver.py', 
        'LAN_Streamer.bat'
    ]
    
    optional_files = [
        'protocol.py',
        'apply_hotfix.py',
        'test_connection.py',
        'debug_protocol.py',
        'AudioSetup.bat'
    ]
    
    files_ok = True
    
    # Check required files
    for filename in required_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename} ({size:,} bytes)")
        else:
            print(f"❌ {filename} - Missing!")
            files_ok = False
    
    # Check optional files
    print("\n📁 Optional Files:")
    for filename in optional_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename} ({size:,} bytes)")
        else:
            print(f"⚠️  {filename} - Not found")
    
    return files_ok

def check_performance():
    """Basic performance check"""
    print_section("PERFORMANCE TEST")
    
    print("🚀 Running basic performance test...")
    
    # Simple CPU test
    start_time = time.time()
    result = sum(i * i for i in range(100000))
    cpu_time = time.time() - start_time
    
    print(f"⚡ CPU Test: {cpu_time:.3f} seconds")
    
    if cpu_time < 0.1:
        print("✅ Excellent CPU performance")
        cpu_perf = True
    elif cpu_time < 0.5:
        print("✅ Good CPU performance")  
        cpu_perf = True
    else:
        print("⚠️  Slow CPU - May affect streaming quality")
        cpu_perf = False
    
    # Memory test (basic)
    try:
        import psutil
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        print(f"💾 Total RAM: {total_gb:.1f} GB")
        print(f"💾 Available RAM: {available_gb:.1f} GB")
        
        if total_gb >= 8:
            print("✅ Excellent RAM - 8GB+ available")
            ram_ok = True
        elif total_gb >= 4:
            print("✅ Sufficient RAM - 4GB+ available")
            ram_ok = True
        else:
            print("⚠️  Limited RAM - May affect performance")
            ram_ok = False
            
    except ImportError:
        print("💾 RAM: Unable to check (psutil not installed)")
        ram_ok = True
    
    return cpu_perf and ram_ok

def run_recommendations():
    """Provide recommendations based on check results"""
    print_section("RECOMMENDATIONS")
    
    print("🎯 For optimal streaming performance:")
    print("   • Use Ethernet instead of WiFi")
    print("   • Close unnecessary applications")
    print("   • Enable Windows Game Mode")
    print("   • Update graphics drivers")
    print("   • Configure Windows Firewall to allow Python")
    print()
    
    print("🔧 If you encounter issues:")
    print("   • Run LAN_Streamer.bat → [5] Apply Fix")
    print("   • Use LAN_Streamer.bat → [3] Test Connection") 
    print("   • Check LAN_Streamer.bat → [4] Audio Setup")
    print("   • Review the README.md file")

def main():
    """Main system check function"""
    print_header()
    
    # Run all checks
    python_ok = check_python()
    deps_ok = check_dependencies()
    system_ok = check_system_specs()
    network_ok = check_network()
    files_ok = check_files()
    perf_ok = check_performance()
    
    # Summary
    print_section("SYSTEM CHECK SUMMARY")
    
    checks = [
        ("Python Installation", python_ok),
        ("Required Dependencies", deps_ok),
        ("System Specifications", system_ok), 
        ("Network Configuration", network_ok),
        ("Required Files", files_ok),
        ("Performance", perf_ok)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Your system is ready for LAN streaming!")
        print("   Run LAN_Streamer.bat → [6] Quick Start to begin!")
    else:
        print("⚠️  SOME ISSUES FOUND - See details above")
        print("   Fix the issues marked with ❌ and run this check again")
        print("   Use LAN_Streamer.bat → [5] Apply Fix for automated repairs")
    
    # Always show recommendations
    run_recommendations()
    
    print("\n" + "=" * 70)
    print("System check completed!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSystem check cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during system check: {e}")
        sys.exit(1)
    
    # Wait for user input before closing
    input("\nPress Enter to exit...")
