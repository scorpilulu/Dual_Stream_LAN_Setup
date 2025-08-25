#!/usr/bin/env python3
"""
DirectX Support Diagnostic Script
Run this on both Windows boots to compare DirectX capabilities
"""

import sys
import os
import subprocess
import platform

def get_system_info():
    """Get basic system information"""
    info = {
        'os': platform.platform(),
        'python': sys.version,
        'architecture': platform.architecture()[0]
    }
    return info

def check_dxdiag_info():
    """Extract DirectX information using dxdiag"""
    print("🔍 Checking DirectX information...")
    
    try:
        # Run dxdiag and save to temp file
        temp_file = "dxdiag_output.txt"
        result = subprocess.run([
            "dxdiag", "/t", temp_file
        ], capture_output=True, text=True, timeout=30)
        
        if os.path.exists(temp_file):
            with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract key information
            lines = content.split('\n')
            dx_info = {}
            
            for line in lines:
                line = line.strip()
                if 'DirectX Version:' in line:
                    dx_info['directx_version'] = line.split(':', 1)[1].strip()
                elif 'Driver Version:' in line and 'display' not in dx_info:
                    dx_info['display_driver'] = line.split(':', 1)[1].strip()
                elif 'Driver Date:' in line and 'driver_date' not in dx_info:
                    dx_info['driver_date'] = line.split(':', 1)[1].strip()
                elif 'Feature Levels:' in line:
                    dx_info['feature_levels'] = line.split(':', 1)[1].strip()
            
            # Clean up
            os.remove(temp_file)
            return dx_info
        else:
            return {"error": "Could not generate dxdiag output"}
            
    except Exception as e:
        return {"error": f"dxdiag failed: {e}"}

def test_dxcam_import():
    """Test if DXCam can be imported and initialized"""
    print("🔍 Testing DXCam import...")
    
    try:
        import dxcam
        print("✅ DXCam imported successfully")
        
        # Test output info
        outputs = dxcam.output_info()
        print(f"✅ Found {len(outputs)} display output(s)")
        
        # Test camera creation
        camera = dxcam.create(output_idx=0, output_color="BGR")
        if camera:
            print("✅ DXCam camera created successfully")
            
            # Test frame capture
            camera.start(target_fps=1)
            frame = camera.get_latest_frame()
            camera.stop()
            
            if frame is not None:
                print(f"✅ Frame capture successful: {frame.shape}")
                return True
            else:
                print("❌ Frame capture failed")
                return False
        else:
            print("❌ DXCam camera creation failed")
            return False
            
    except ImportError:
        print("❌ DXCam not installed")
        return False
    except Exception as e:
        print(f"❌ DXCam error: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 DIRECTX SUPPORT DIAGNOSTIC")
    print("=" * 60)
    
    # System info
    print("\n📋 SYSTEM INFORMATION:")
    print("-" * 30)
    system_info = get_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    # DirectX info
    print("\n📋 DIRECTX INFORMATION:")
    print("-" * 30)
    dx_info = check_dxdiag_info()
    for key, value in dx_info.items():
        print(f"{key}: {value}")
    
    # DXCam test
    print("\n📋 DXCAM TEST:")
    print("-" * 30)
    dxcam_works = test_dxcam_import()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if dxcam_works:
        print("🎉 DXCam is working on this boot!")
        print("This boot has proper DirectX/graphics driver support")
    else:
        print("⚠️  DXCam is NOT working on this boot")
        print("This boot needs graphics driver/DirectX updates")
    
    print(f"\nBoot identifier: {platform.node()}-{platform.platform()}")
    
    # Save results
    with open(f"dx_test_results_{platform.node()}.txt", 'w') as f:
        f.write("DirectX Diagnostic Results\n")
        f.write("=" * 30 + "\n")
        for key, value in {**system_info, **dx_info}.items():
            f.write(f"{key}: {value}\n")
        f.write(f"\nDXCam Working: {dxcam_works}\n")
    
    print(f"\n📄 Results saved to: dx_test_results_{platform.node()}.txt")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n\nError during test: {e}")
    
    input("\nPress Enter to exit...")