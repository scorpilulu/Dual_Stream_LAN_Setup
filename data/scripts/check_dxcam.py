"""
DXCam Diagnostic Tool for LAN Screen Streamer
Helps troubleshoot screen capture issues
"""
import sys
import os

def check_dxcam():
    """Check if dxcam is installed and working"""
    print("=" * 60)
    print("DXCAM DIAGNOSTIC TOOL")
    print("=" * 60)
    print()
    
    # Check if dxcam is installed
    print("1. Checking DXCam installation...")
    try:
        import dxcam
        print("   ✓ DXCam is installed")
    except ImportError:
        print("   ✗ DXCam is NOT installed!")
        print("   Run: pip install dxcam")
        return False
    
    print()
    print("2. Checking available displays...")
    try:
        outputs = dxcam.output_info()
        if outputs:
            print(f"   ✓ Found {len(outputs)} display output(s):")
            for i, output in enumerate(outputs):
                print(f"      Output {i}: {output}")
        else:
            print("   ✗ No display outputs detected!")
            print("   Possible causes:")
            print("   - No monitor connected")
            print("   - Running via Remote Desktop")
            print("   - GPU driver issues")
            return False
    except Exception as e:
        print(f"   ✗ Error listing outputs: {e}")
        return False
    
    print()
    print("3. Testing screen capture...")
    try:
        camera = dxcam.create(output_idx=0, output_color="BGR")
        if camera:
            print("   ✓ Screen capture initialized successfully!")
            
            # Try to capture a frame
            camera.start(target_fps=30)
            frame = camera.get_latest_frame()
            camera.stop()
            del camera
            
            if frame is not None:
                print(f"   ✓ Test capture successful! Frame size: {frame.shape}")
                return True
            else:
                print("   ✗ Could not capture frame")
                return False
        else:
            print("   ✗ Failed to create capture device")
            return False
    except Exception as e:
        error_msg = str(e)
        print(f"   ✗ Capture failed: {error_msg}")
        
        if "device interface or feature level is not supported" in error_msg.lower():
            print()
            print("   DIAGNOSIS: DirectX Desktop Duplication not supported")
            print()
            print("   SOLUTIONS:")
            print("   1. Update your graphics driver:")
            print("      - Intel: https://www.intel.com/content/www/us/en/support")
            print("      - NVIDIA: https://www.nvidia.com/drivers")
            print("      - AMD: https://www.amd.com/en/support")
            print()
            print("   2. Check Windows version:")
            print("      - Requires Windows 8 or newer")
            print("      - Windows 10/11 recommended")
            print()
            print("   3. Ensure a monitor is connected:")
            print("      - Physical monitor or HDMI dummy plug")
            print("      - Not via Remote Desktop")
            print()
            print("   4. Run dxdiag to check DirectX:")
            print("      - Press Win+R, type 'dxdiag', press Enter")
            print("      - Check Display tab for Feature Levels")
            print("      - Need Feature Level 10_0 or higher")
        
        return False
    
    print()
    print("=" * 60)
    print("RESULT: All checks passed! DXCam is ready to use.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    print()
    success = check_dxcam()
    print()
    
    if not success:
        print("Press Enter to exit...")
        input()
        sys.exit(1)
    else:
        print("Press Enter to exit...")
        input()
        sys.exit(0)
