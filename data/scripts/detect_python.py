"""
Smart Python Detector - Finds Python installations on Windows
"""
import os
import sys
import subprocess
import glob
import json
from pathlib import Path

def find_python_installations():
    """Find all Python installations on the system"""
    pythons = []
    
    # Common Python installation paths on Windows
    common_paths = [
        # User installations
        os.path.expanduser("~\\AppData\\Local\\Programs\\Python\\Python*"),
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\WindowsApps"),
        
        # System-wide installations
        "C:\\Python*",
        "C:\\Program Files\\Python*",
        "C:\\Program Files (x86)\\Python*",
        
        # Anaconda/Miniconda
        os.path.expanduser("~\\Anaconda3"),
        os.path.expanduser("~\\Miniconda3"),
        "C:\\ProgramData\\Anaconda3",
        "C:\\ProgramData\\Miniconda3",
        
        # Microsoft Store Python
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.*"),
        
        # Common custom locations
        "C:\\Tools\\Python*",
        "D:\\Python*",
        "E:\\Python*",
    ]
    
    # Search for Python executables
    for pattern in common_paths:
        for path in glob.glob(pattern):
            # Look for python.exe in the directory
            python_exe = os.path.join(path, "python.exe")
            if os.path.exists(python_exe):
                pythons.append(python_exe)
            
            # Also check Scripts folder
            python_exe = os.path.join(path, "Scripts", "python.exe")
            if os.path.exists(python_exe):
                pythons.append(python_exe)
    
    # Also check if python is in PATH
    try:
        result = subprocess.run(["where", "python"], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line and os.path.exists(line):
                    pythons.append(line)
    except:
        pass
    
    # Try python3 command as well
    try:
        result = subprocess.run(["where", "python3"], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line and os.path.exists(line):
                    pythons.append(line)
    except:
        pass
    
    # Remove duplicates while preserving order
    seen = set()
    unique_pythons = []
    for python in pythons:
        normalized = os.path.normpath(python).lower()
        if normalized not in seen:
            seen.add(normalized)
            unique_pythons.append(python)
    
    return unique_pythons

def get_python_version(python_path):
    """Get version info for a Python installation"""
    try:
        result = subprocess.run(
            [python_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().replace("Python ", "")
            return version
    except:
        pass
    return None

def check_modules(python_path):
    """Check if required modules are installed"""
    modules = ["cv2", "numpy", "PIL", "dxcam", "pyaudio"]
    installed = []
    missing = []
    
    for module in modules:
        try:
            result = subprocess.run(
                [python_path, "-c", f"import {module}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                installed.append(module)
            else:
                missing.append(module)
        except:
            missing.append(module)
    
    return installed, missing

def main():
    print("Scanning for Python installations...")
    print("-" * 50)
    
    pythons = find_python_installations()
    
    if not pythons:
        print("No Python installations found!")
        print("\nPython needs to be installed.")
        print("Download from: https://www.python.org/downloads/")
        return None
    
    valid_pythons = []
    
    for i, python_path in enumerate(pythons, 1):
        version = get_python_version(python_path)
        if version:
            print(f"\n{i}. Found Python {version}")
            print(f"   Path: {python_path}")
            
            # Check if version is 3.8+
            try:
                major, minor = version.split('.')[:2]
                if int(major) >= 3 and int(minor) >= 8:
                    installed, missing = check_modules(python_path)
                    print(f"   Modules: {len(installed)}/{len(installed)+len(missing)} installed")
                    
                    valid_pythons.append({
                        "path": python_path,
                        "version": version,
                        "installed_modules": installed,
                        "missing_modules": missing,
                        "ready": len(missing) == 0
                    })
                else:
                    print(f"   Status: Too old (need 3.8+)")
            except:
                pass
    
    if not valid_pythons:
        print("\nNo suitable Python installation found (need 3.8+)")
        return None
    
    # Find the best Python (one with most modules installed)
    best_python = max(valid_pythons, key=lambda x: len(x["installed_modules"]))
    
    print("\n" + "=" * 50)
    print("RECOMMENDED Python installation:")
    print(f"Version: {best_python['version']}")
    print(f"Path: {best_python['path']}")
    
    if best_python['ready']:
        print("Status: ✓ Ready to use!")
    else:
        print(f"Status: Missing modules: {', '.join(best_python['missing_modules'])}")
    
    # Save the result
    with open("python_config.json", "w") as f:
        json.dump(best_python, f, indent=2)
    
    return best_python['path']

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\nSelected Python: {result}")
        sys.exit(0)
    else:
        sys.exit(1)
