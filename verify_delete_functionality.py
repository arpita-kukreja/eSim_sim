#!/usr/bin/env python3
"""
Verification script for eSim delete to trash functionality
Run this script to verify that the delete to trash feature is working correctly.
"""

import os
import sys
import tempfile
import subprocess

def check_send2trash_availability():
    """Check if send2trash is available in the current environment"""
    try:
        import send2trash
        print("✓ send2trash library is available")
        return True
    except ImportError:
        print("✗ send2trash library is NOT available")
        return False

def check_virtual_environment():
    """Check if we're running in a virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in a virtual environment")
        return True
    else:
        print("✗ Not running in a virtual environment")
        return False

def test_send2trash_functionality():
    """Test the actual send2trash functionality"""
    if not check_send2trash_availability():
        return False
    
    try:
        import send2trash
        
        # Create a temporary test directory
        test_dir = tempfile.mkdtemp(prefix="esim_test_delete_")
        test_file = os.path.join(test_dir, "test_file.txt")
        
        # Create a test file
        with open(test_file, 'w') as f:
            f.write("Test content for delete to trash")
        
        print(f"Created test directory: {test_dir}")
        
        # Send to trash
        send2trash.send2trash(test_dir)
        print("✓ Successfully sent to trash")
        
        # Check if files are no longer in original location
        if not os.path.exists(test_dir):
            print("✓ Files removed from original location")
        else:
            print("✗ Files still exist in original location")
            return False
        
        # Check if files are in trash
        trash_path = os.path.expanduser("~/.local/share/Trash/files/")
        if os.path.exists(trash_path):
            trash_files = os.listdir(trash_path)
            test_dir_name = os.path.basename(test_dir)
            
            if test_dir_name in trash_files:
                print("✓ Files found in trash")
                return True
            else:
                print("✗ Files not found in trash")
                return False
        else:
            print("✗ Trash directory does not exist")
            return False
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        return False

def check_esim_environment():
    """Check if eSim environment is properly set up"""
    print("\n=== eSim Environment Check ===")
    
    # Check if we're in the eSim directory
    if os.path.exists("src/frontEnd/ProjectExplorer.py"):
        print("✓ eSim source code found")
    else:
        print("✗ eSim source code not found - make sure you're in the eSim directory")
        return False
    
    # Check virtual environment
    venv_found = False
    for venv_name in ["venv311", "venv", "esim_venv"]:
        if os.path.exists(f"{venv_name}/bin/activate"):
            print(f"✓ Virtual environment found: {venv_name}")
            venv_found = True
            break
    
    if not venv_found:
        print("✗ No virtual environment found")
        return False
    
    return True

def main():
    """Main verification function"""
    print("eSim Delete to Trash Functionality Verification")
    print("=" * 50)
    
    # Check eSim environment
    if not check_esim_environment():
        print("\nPlease make sure you're running this script from the eSim directory.")
        return
    
    print("\n=== send2trash Library Check ===")
    send2trash_available = check_send2trash_availability()
    
    print("\n=== Virtual Environment Check ===")
    venv_check = check_virtual_environment()
    
    print("\n=== Functionality Test ===")
    if send2trash_available:
        functionality_test = test_send2trash_functionality()
    else:
        print("Skipping functionality test - send2trash not available")
        functionality_test = False
    
    print("\n=== Summary ===")
    if send2trash_available and functionality_test:
        print("✓ All checks passed! Delete to trash should work correctly.")
        print("\nTo use delete to trash in eSim:")
        print("1. Make sure you're running eSim from the virtual environment")
        print("2. Right-click on a project in the Project Explorer")
        print("3. Select 'Delete Project'")
        print("4. Choose 'Send to Trash' option")
    else:
        print("✗ Some checks failed. Delete to trash may not work correctly.")
        print("\nTroubleshooting:")
        if not send2trash_available:
            print("- Install send2trash: pip install send2trash")
        if not venv_check:
            print("- Make sure you're running eSim from the virtual environment")
        if not functionality_test:
            print("- There may be permission issues with the trash directory")
    
    print("\n=== Running eSim ===")
    print("To run eSim with the correct environment:")
    print("1. Activate the virtual environment: source venv311/bin/activate")
    print("2. Run eSim: python src/frontEnd/Application.py")
    print("   or use the launcher: ./run_esim.sh")

if __name__ == "__main__":
    main() 