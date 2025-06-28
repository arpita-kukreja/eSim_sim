#!/usr/bin/env python3
"""
Customize Tab Colors in eSim
This script demonstrates how to change the tab colors in eSim.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from frontEnd.tab_colors_config import (
    DARK_TAB_COLORS, LIGHT_TAB_COLORS, 
    PURPLE_TAB_COLORS, GREEN_TAB_COLORS, ORANGE_TAB_COLORS,
    apply_custom_tab_colors, get_tab_stylesheet
)

def main():
    """Main function to demonstrate tab color customization."""
    
    print("🎨 eSim Tab Color Customization")
    print("=" * 40)
    
    print("\n📋 Available Color Schemes:")
    print("1. Default Dark Theme (Blue)")
    print("2. Default Light Theme (Blue)")
    print("3. Purple Theme")
    print("4. Green Theme")
    print("5. Orange Theme")
    
    print("\n🔧 How to Apply Custom Colors:")
    print("-" * 30)
    
    print("\n1. Import the configuration:")
    print("from frontEnd.tab_colors_config import apply_custom_tab_colors, PURPLE_TAB_COLORS")
    
    print("\n2. Apply purple theme to dark mode:")
    print("apply_custom_tab_colors(app, dark_colors=PURPLE_TAB_COLORS)")
    
    print("\n3. Apply green theme to light mode:")
    print("apply_custom_tab_colors(app, light_colors=GREEN_TAB_COLORS)")
    
    print("\n4. Apply both themes:")
    print("apply_custom_tab_colors(app, dark_colors=PURPLE_TAB_COLORS, light_colors=GREEN_TAB_COLORS)")
    
    print("\n🎯 Quick Color Changes:")
    print("-" * 25)
    
    # Show the current dark theme colors
    print("\nCurrent Dark Theme Colors:")
    for key, value in DARK_TAB_COLORS.items():
        if isinstance(value, dict):
            print(f"  {key}: {value['start']} → {value['end']}")
        else:
            print(f"  {key}: {value}")
    
    print("\nPurple Theme Colors:")
    for key, value in PURPLE_TAB_COLORS.items():
        if isinstance(value, dict):
            print(f"  {key}: {value['start']} → {value['end']}")
        else:
            print(f"  {key}: {value}")
    
    print("\n💡 Tips:")
    print("- Use hex color codes (e.g., '#ff6b6b')")
    print("- Ensure good contrast between text and background")
    print("- Test both selected and unselected states")
    print("- Consider accessibility (colorblind-friendly)")
    
    print("\n🔗 Integration with eSim:")
    print("- Add the import to your main application file")
    print("- Call apply_custom_tab_colors() after creating the main window")
    print("- The colors will automatically switch with theme changes")

if __name__ == "__main__":
    main() 