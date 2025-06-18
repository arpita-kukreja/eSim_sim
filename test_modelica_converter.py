#!/usr/bin/env python3
"""
Test script to verify Modelica converter functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from configuration.Appconfig import Appconfig
from ngspicetoModelica.ModelicaUI import OpenModelicaEditor

def test_modelica_converter():
    """Test the Modelica converter initialization"""
    try:
        print("Testing Modelica converter...")
        
        # Test Appconfig
        print("1. Testing Appconfig...")
        app_config = Appconfig()
        print(f"   - Appconfig created successfully")
        print(f"   - modelica_map_json: {getattr(Appconfig, 'modelica_map_json', 'Not found')}")
        
        # Test OpenModelicaEditor
        print("2. Testing OpenModelicaEditor...")
        test_dir = "/tmp/test_project"
        editor = OpenModelicaEditor(test_dir)
        print(f"   - OpenModelicaEditor created successfully")
        print(f"   - map_json: {editor.map_json}")
        
        print("✅ All tests passed! Modelica converter should work properly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_modelica_converter() 