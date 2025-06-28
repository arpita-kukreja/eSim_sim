# Dark Theme Plotting Issue - Analysis and Fix

## Problem Description

In eSim, when using dark theme, the plots were not displaying correctly with dark backgrounds. The plots appeared with light backgrounds or were not visible at all, making it difficult to view simulation results in dark mode.

## Root Cause Analysis

After examining the codebase, several issues were identified:

### 1. **Theme Propagation Issue**
- The main application defaulted to light theme (`self.is_dark_theme = False`)
- The plotting window wasn't properly receiving the current theme setting
- Theme changes weren't being propagated correctly to the plotting components

### 2. **Plot Theme Update Timing**
- The `update_plot_theme()` method was called during initialization
- However, when new plots were drawn (in functions like `onPush_decade`, `onPush_ac`, etc.), the theme settings were not reapplied
- The axes were cleared with `self.axes.cla()` but theme wasn't reapplied

### 3. **Missing Theme Reapplication**
- Plotting functions cleared the axes but didn't reapply dark theme settings
- This caused plots to revert to default matplotlib styling
- Axis labels and grid weren't using theme colors

### 4. **Color Palette Issues**
- The original color palette wasn't optimized for dark theme visibility
- Some colors had poor contrast against dark backgrounds

## Applied Fixes

### 1. **Fixed Theme Reapplication in Plotting Functions**

**Files Modified:** `src/ngspiceSimulation/pythonPlotting.py`

**Changes:**
- Added `self.update_plot_theme()` calls after plotting in all plotting functions:
  - `onPush_decade()`
  - `onPush_ac()`
  - `onPush_trans()`
  - `onPush_dc()`
  - `pushedClear()`
  - `pushedPlotFunc()`

**Code Example:**
```python
def onPush_decade(self):
    # ... plotting code ...
    
    # Reapply theme after plotting
    self.update_plot_theme()
    self.canvas.draw()
```

### 2. **Improved Theme Propagation**

**Files Modified:** `src/frontEnd/DockArea.py`

**Changes:**
- Enhanced `plottingEditor()` to properly detect the main application's current theme
- Added logic to traverse the widget hierarchy to find the main window
- Ensured the correct theme is passed to the plotting window

**Code Example:**
```python
# Get the current theme from the main application
main_window = None
current_widget = self
while current_widget.parent() is not None:
    current_widget = current_widget.parent()
    if hasattr(current_widget, 'is_dark_theme'):
        main_window = current_widget
        break

is_dark_theme = getattr(main_window, 'is_dark_theme', False) if main_window else False
```

### 3. **Enhanced Color Palette**

**Files Modified:** `src/ngspiceSimulation/pythonPlotting.py`

**Changes:**
- Updated the color palette to use brighter, more contrasting colors
- Changed from: `['#ff7e76', '#36d399', '#51b4ff', '#ffd666', '#bd93f9', '#ff79c6', '#8be9fd']`
- Changed to: `['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#a55eea', '#fd79a8', '#00d2d3']`

### 4. **Improved Theme Update Method**

**Files Modified:** `src/ngspiceSimulation/pythonPlotting.py`

**Changes:**
- Enhanced `update_plot_theme()` to handle legend colors
- Added proper legend background and text color updates
- Ensured all plot elements use theme-appropriate colors

**Code Example:**
```python
# Update legend colors if it exists
if self.axes.get_legend():
    legend = self.axes.get_legend()
    legend.get_frame().set_facecolor(bg_color)
    legend.get_frame().set_edgecolor(accent_color)
    for text in legend.get_texts():
        text.set_color(text_color)
```

### 5. **Added Legend Support**

**Files Modified:** `src/ngspiceSimulation/pythonPlotting.py`

**Changes:**
- Added `self.axes.legend()` calls to all plotting functions
- Ensured legends are displayed with proper theme colors
- Improved plot readability in both light and dark themes

### 6. **Fixed Axis Label Colors**

**Files Modified:** `src/ngspiceSimulation/pythonPlotting.py`

**Changes:**
- Updated all axis labels to use theme colors
- Added proper font styling for better visibility
- Ensured consistent color scheme across all plot elements

## Testing

A test script (`test_dark_theme_plot.py`) was created to verify the fixes:

```bash
python test_dark_theme_plot.py
```

The test script:
- Creates sample simulation data
- Tests the plotting window with dark theme enabled
- Verifies that plots are visible and properly themed
- Shows the window for 5 seconds to allow visual inspection

## Expected Results

After applying these fixes:

1. **Dark Theme Plots**: Plots should now display with dark backgrounds when dark theme is enabled
2. **Proper Colors**: All plot elements (axes, labels, grid, legends) should use theme-appropriate colors
3. **Consistent Theming**: Theme changes should be properly propagated to all plotting windows
4. **Better Visibility**: Plot lines should be clearly visible against dark backgrounds
5. **Legend Support**: Legends should be displayed with proper dark theme styling

## Files Modified

1. `src/ngspiceSimulation/pythonPlotting.py` - Main plotting functionality
2. `src/frontEnd/DockArea.py` - Theme propagation
3. `test_dark_theme_plot.py` - Test script (new file)
4. `DARK_THEME_PLOT_FIX.md` - This documentation (new file)

## Usage

To use the fixed dark theme plotting:

1. Enable dark theme in eSim (Ctrl+T or theme toggle button)
2. Run a simulation
3. Open the plotting window
4. Plots should now display with proper dark theme styling

The fixes ensure that the plotting functionality works correctly in both light and dark themes, with proper color contrast and visibility. 