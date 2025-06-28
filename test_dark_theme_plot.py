#!/usr/bin/env python3
"""
Test script to verify dark theme plotting functionality in eSim.
This script tests the plotWindow class with dark theme enabled.
"""

import sys
import os
import numpy as np
from PyQt5 import QtWidgets, QtCore

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_data():
    """Create test simulation data files."""
    # Create a test project directory
    test_dir = "test_project"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test plot data files
    x_data = np.linspace(0, 10, 100)
    y1_data = np.sin(x_data) * 5
    y2_data = np.cos(x_data) * 3
    y3_data = np.exp(-x_data/5) * 4
    
    # Write voltage data
    with open(os.path.join(test_dir, "plot_data_v.txt"), "w") as f:
        f.write("Node1 Node2\n")
        for i in range(len(x_data)):
            f.write(f"{x_data[i]:.6f} {y1_data[i]:.6f} {y2_data[i]:.6f}\n")
    
    # Write current data
    with open(os.path.join(test_dir, "plot_data_i.txt"), "w") as f:
        f.write("Branch1\n")
        for i in range(len(x_data)):
            f.write(f"{y3_data[i]:.6f}\n")
    
    # Create analysis file
    with open(os.path.join(test_dir, "analysis"), "w") as f:
        f.write("Transient Analysis\n")
        f.write("Time\n")
        f.write("Node1 Node2 Branch1\n")
    
    return test_dir

def test_dark_theme_plotting():
    """Test the dark theme plotting functionality."""
    app = QtWidgets.QApplication(sys.argv)
    
    # Create test data
    test_dir = create_test_data()
    
    try:
        # Import the plotting module
        from ngspiceSimulation.pythonPlotting import plotWindow
        
        # Test with dark theme
        print("Testing dark theme plotting...")
        plot_window = plotWindow.add_output(test_dir, "test_project", is_dark_theme=True)
        
        # Check if the window was created successfully
        if plot_window:
            print("✓ Plot window created successfully with dark theme")
            
            # Check if theme is applied correctly
            if plot_window.is_dark_theme:
                print("✓ Dark theme is enabled")
            else:
                print("✗ Dark theme is not enabled")
            
            # Show the window
            plot_window.show()
            
            # Run the application for a few seconds to see the result
            print("Showing plot window for 5 seconds...")
            QtCore.QTimer.singleShot(5000, app.quit)
            app.exec_()
            
        else:
            print("✗ Failed to create plot window")
            
    except Exception as e:
        print(f"✗ Error testing dark theme plotting: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test files
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_dark_theme_plotting() 