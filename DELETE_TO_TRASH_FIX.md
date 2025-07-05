# eSim Delete to Trash Implementation

## Overview
This document describes the implementation of the "Delete to Trash" functionality in eSim, which allows users to safely delete projects by moving them to the system trash instead of permanently deleting them.

## Implementation Details

### 1. Dependencies
- **send2trash**: Python library for moving files to system trash
- **shutil**: For permanent deletion (fallback)
- **os**: For file system operations

### 2. Code Structure

#### Imports and Setup
```python
import shutil
from PyQt5 import QtCore, QtWidgets

# Try to import send2trash for trash functionality
try:
    import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False
```

#### Menu Integration
The delete functionality is integrated into the project context menu:
```python
deleteProject = menu.addAction(self.tr("Delete Project"))
deleteProject.triggered.connect(self.deleteProject)
```

#### Core Delete Method
The `deleteProject()` method provides:
- **Path validation**: Checks if project exists before attempting deletion
- **User choice**: Offers "Move to Trash" or "Delete Permanently" options
- **Error handling**: Comprehensive error handling for various scenarios
- **UI updates**: Removes project from tree view and configuration
- **User feedback**: Clear success/error messages

### 3. User Experience

#### When send2trash is available:
1. Right-click on a project
2. Select "Delete Project"
3. Choose from:
   - **"Move to Trash"** (recommended) - Moves project to system trash
   - **"Delete Permanently"** - Permanently removes the project
   - **"Cancel"** - Cancels the operation

#### When send2trash is not available:
1. Right-click on a project
2. Select "Delete Project"
3. Choose from:
   - **"Delete Permanently"** - Permanently removes the project
   - **"Cancel"** - Cancels the operation

### 4. Error Handling

The implementation handles various error scenarios:
- **PermissionError**: When user lacks write permissions
- **OSError**: General file system errors
- **Exception**: Unexpected errors with detailed messages

### 5. Configuration Updates

When a project is deleted:
- Removed from the project explorer tree view
- Removed from the application configuration
- Configuration file is updated on disk
- Current project is cleared if it was the deleted project

## Usage Instructions

### 1. Start eSim
```bash
./run_esim_with_trash.sh
```

### 2. Delete a Project
1. Right-click on a project in the Project Explorer
2. Select "Delete Project"
3. Choose your preferred deletion method
4. Confirm the action

### 3. Verify Deletion
- **Move to Trash**: Check your system trash (usually `~/.local/share/Trash/files/`)
- **Delete Permanently**: Project is completely removed from disk

## Technical Notes

### Trash Location
- **Linux**: `~/.local/share/Trash/files/`
- **macOS**: `~/.Trash/`
- **Windows**: `C:\$Recycle.Bin\`

### Dependencies
- `send2trash==1.8.2` is included in `requirements.txt`
- Automatically installed when using the launcher scripts

### Fallback Behavior
If `send2trash` is not available, the system defaults to permanent deletion with a clear warning to the user.

## Testing

### Verification Script
Run the verification script to ensure everything works:
```bash
source venv311/bin/activate
python verify_delete_functionality.py
```

### Manual Testing
1. Create a test project
2. Right-click and select "Delete Project"
3. Choose "Move to Trash"
4. Verify the project appears in your system trash
5. Verify the project is removed from eSim

## Troubleshooting

### Common Issues

1. **"Move to Trash" option not appearing**
   - Ensure you're running eSim from the virtual environment
   - Check that `send2trash` is installed: `pip install send2trash`

2. **Permission errors**
   - Ensure you have write permissions to the project directory
   - Close any applications that might be using the project files

3. **Projects not moving to trash**
   - Check if your system trash directory exists and is writable
   - Verify the `send2trash` library is working correctly

### Debug Information
The implementation includes comprehensive error messages that will help identify issues when they occur.

## Files Modified

- `src/frontEnd/ProjectExplorer.py`: Added delete functionality with trash support
- `requirements.txt`: Added send2trash dependency
- `run_esim.sh`: Updated to ensure proper environment
- `run_esim_with_trash.sh`: Enhanced launcher script
- `verify_delete_functionality.py`: Verification script

## Summary

This implementation provides a clean, user-friendly way to delete projects in eSim with the option to move them to trash for safe recovery. The code is robust, handles errors gracefully, and provides clear feedback to users. 