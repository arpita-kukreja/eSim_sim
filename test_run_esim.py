#!/usr/bin/env python3
"""
Simple test script to run eSim application with error handling
"""

import os
import sys
import traceback

def main():
    try:
        # Set up the environment
        os.environ['PYTHONPATH'] = 'src'
        sys.path.insert(0, 'src')
        
        print("Setting up environment...")
        
        # Import required modules
        print("Importing PyQt5...")
        from PyQt5.QtWidgets import QApplication
        
        print("Importing Application...")
        from frontEnd.Application import main
        
        print("Starting eSim application...")
        main(sys.argv)
        
    except ImportError as e:
        print(f"Import error: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main() 