# =========================================================================
#          FILE: Application.py
#
#         USAGE: ---
#
#   DESCRIPTION: This main file use to start the Application
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Fahim Khan, fahim.elex@gmail.com
#    MAINTAINED: Rahul Paknikar, rahulp@iitb.ac.in
#                Sumanto Kar, sumantokar@iitb.ac.in
#                Pranav P, pranavsdreams@gmail.com
#  ORGANIZATION: eSim Team at FOSSEE, IIT Bombay
#       CREATED: Tuesday 24 February 2015
#      REVISION: Wednesday 07 June 2023

# =========================================================================

import os
import sys
import traceback
import webbrowser

if os.name == 'nt':
    from frontEnd import pathmagic  # noqa:F401
    init_path = ''
else:
    import pathmagic    # noqa:F401
    init_path = '../../'

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.Qt import QSize
from configuration.Appconfig import Appconfig
from frontEnd import ProjectExplorer
from frontEnd import Workspace
from frontEnd import DockArea
from projManagement.openProject import OpenProjectInfo
from projManagement.newProject import NewProjectInfo
from projManagement.Kicad import Kicad
from projManagement.Validation import Validation
from projManagement import Worker
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# Its our main window of application.


class Application(QtWidgets.QMainWindow):
    """This class initializes all objects used in this file."""
    global project_name
    simulationEndSignal = QtCore.pyqtSignal(QtCore.QProcess.ExitStatus, int)

    def __init__(self, *args):
        """Initialize main Application window."""

        # Calling __init__ of super class
        QtWidgets.QMainWindow.__init__(self, *args)

        # Theme state - set light theme as default
        self.is_dark_theme = False

        # Initialize font sizes
        self.toolbar_font_size = 10
        self.text_font_size = 10
        self.left_toolbar_font_size = 9  # Specific size for left toolbar buttons
        self.top_toolbar_font_size = 10  # Specific size for top toolbar buttons
        # Initialize icon sizes
        self.top_toolbar_icon_size = 24  # px
        self.left_toolbar_icon_size = 24  # px
        self.top_toolbar_icon_min = 16
        self.top_toolbar_icon_max = 96  # Increased from 56
        self.left_toolbar_icon_min = 16
        self.left_toolbar_icon_max = 96  # Increased from 56
        self.toolbar_icon_step = 2

        # Set slot for simulation end signal to plot simulation data
        self.simulationEndSignal.connect(self.plotSimulationData)

        #the plotFlag
        self.plotFlag = False

        # Creating require Object
        self.obj_workspace = Workspace.Workspace()
        self.obj_Mainview = MainView(self.is_dark_theme)
        self.obj_kicad = Kicad(self.obj_Mainview.obj_dockarea)
        self.obj_appconfig = Appconfig()
        self.obj_validation = Validation()
        
        # Initialize all widget
        self.setCentralWidget(self.obj_Mainview)
        self.initToolBar()

        self.setGeometry(self.obj_appconfig._app_xpos,
                         self.obj_appconfig._app_ypos,
                         self.obj_appconfig._app_width,
                         self.obj_appconfig._app_heigth)
        self.setWindowTitle(
            self.obj_appconfig._APPLICATION + "-" + self.obj_appconfig._VERSION
        )
        self.showMaximized()
        self.setWindowIcon(QtGui.QIcon(init_path + 'images/logo.png'))

        # Apply light theme by default
        self.apply_light_theme()

        self.systemTrayIcon = QtWidgets.QSystemTrayIcon(self)
        self.systemTrayIcon.setIcon(QtGui.QIcon(init_path + 'images/logo.png'))
        self.systemTrayIcon.setVisible(True)

        # Set initial font
        self.update_font_sizes()

        self.statusBar = self.statusBar()
        self.statusBar.showMessage('Welcome to eSim!')
        
        # Initialize simulation process
        self.simulation_process = QtCore.QProcess()
        self.simulation_process.readyReadStandardOutput.connect(self.handle_simulation_output)
        self.simulation_process.readyReadStandardError.connect(self.handle_simulation_error)
        self.simulation_process.finished.connect(self.handle_simulation_finished)

        # Add keyboard shortcuts for font size adjustment
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl++"), self, self.increase_font_size)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+-"), self, self.decrease_font_size)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+0"), self, self.reset_font_size)
        
        # Add specific keyboard shortcuts for toolbar font control
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Up"), self, self.increase_toolbar_font_size)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Down"), self, self.decrease_toolbar_font_size)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+0"), self, self.reset_toolbar_font_size)

        # Add helpful message about font size controls
        self.obj_appconfig.print_info("Font size controls:")
        self.obj_appconfig.print_info("  Ctrl++ / Ctrl+- / Ctrl+0: Adjust all font sizes")
        self.obj_appconfig.print_info("  Ctrl+Up / Ctrl+Down / Ctrl+Shift+0: Adjust toolbar button sizes")

        self.current_makerchip_widget = None  # Reference to open makerchip widget
        self.current_modeleditor_widget = None  # Reference to open model editor widget
        self.current_terminalui_widget = None  # Reference to open simulation TerminalUi widget

    def update_font_sizes(self):
        """Update font sizes for all relevant widgets"""
        # Update toolbar fonts
        toolbar_font = QtGui.QFont("Fira Sans", self.toolbar_font_size)
        for toolbar in self.findChildren(QtWidgets.QToolBar):
            toolbar.setFont(toolbar_font)
            for action in toolbar.actions():
                action.setFont(toolbar_font)
            # Update icon size for top toolbar
            toolbar.setIconSize(QSize(self.top_toolbar_icon_size, self.top_toolbar_icon_size))
        # Update left toolbar tool buttons' icon size
        if hasattr(self, 'toolButtons'):
            for button in self.toolButtons:
                button.setIconSize(QSize(self.left_toolbar_icon_size, self.left_toolbar_icon_size))

        # Update text area fonts
        text_font = QtGui.QFont("Fira Code", self.text_font_size)
        
        # Update console (noteArea)
        self.obj_Mainview.noteArea.setFont(text_font)
        
        # Update welcome message font size
        welcome_font_size = self.text_font_size + 2  # Slightly larger for welcome message
        if self.is_dark_theme:
            self.obj_Mainview.noteArea.setStyleSheet(f"""
                QTextEdit {{
                    font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                    line-height: 1.4;
                    padding: 16px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #23273a, stop:1 #181b24);
                    color: #e8eaed;
                    border: 1px solid #23273a;
                    border-radius: 12px;
                    font-size: {welcome_font_size}px;
                }}
            """)
        else:
            self.obj_Mainview.noteArea.setStyleSheet(f"""
                QTextEdit {{
                    font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                    line-height: 1.4;
                    padding: 16px;
                    background: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #e1e4e8;
                    border-radius: 12px;
                    font-size: {welcome_font_size}px;
                }}
            """)
        
        # Update welcome page font size in dock widgets
        for dock_widget in self.findChildren(QtWidgets.QDockWidget):
            if dock_widget.windowTitle().startswith('Welcome'):
                welcome_widget = dock_widget.widget()
                if welcome_widget:
                    welcome_browser = welcome_widget.findChild(QtWidgets.QWidget).findChild(QtWidgets.QTextBrowser)
                    if welcome_browser:
                        welcome_browser.setFont(text_font)
        
        # Update project explorer with smaller font size for better visibility
        project_explorer_font = QtGui.QFont("Fira Code", max(8, self.text_font_size - 3))
        self.obj_Mainview.obj_projectExplorer.setFont(project_explorer_font)
        
        # Update project tree items with smaller font
        project_tree = self.obj_Mainview.obj_projectExplorer.findChild(QtWidgets.QTreeWidget)
        if project_tree:
            project_tree.setFont(project_explorer_font)
            # Update all items in the tree with smaller font
            for i in range(project_tree.topLevelItemCount()):
                item = project_tree.topLevelItem(i)
                item.setFont(0, project_explorer_font)
                # Update child items
                for j in range(item.childCount()):
                    child = item.child(j)
                    child.setFont(0, project_explorer_font)
                    # Update grandchild items
                    for k in range(child.childCount()):
                        grandchild = child.child(k)
                        grandchild.setFont(0, project_explorer_font)

        # Update dock area contents
        dock_area = self.obj_Mainview.obj_dockarea
        for dock in dock_area.findChildren(QtWidgets.QDockWidget):
            dock.setFont(text_font)
            # Update dock widget contents
            dock_widget = dock.widget()
            if dock_widget:
                dock_widget.setFont(text_font)
                # Update all child widgets
                for child in dock_widget.findChildren(QtWidgets.QWidget):
                    if hasattr(child, 'setFont'):
                        child.setFont(text_font)

        # Update status bar
        if hasattr(self, 'statusBar') and isinstance(self.statusBar, QtWidgets.QStatusBar):
            self.statusBar.setFont(text_font)

        # Update toolbar button styling with dynamic font sizes
        self.update_toolbar_button_styling()

        # Force update of all widgets
        self.obj_Mainview.update()
        self.obj_Mainview.obj_projectExplorer.update()
        self.obj_Mainview.obj_dockarea.update()

    def update_toolbar_button_styling(self):
        """Update the styling of toolbar buttons with current font sizes and icon sizes"""
        # Update top toolbar button styling
        if hasattr(self, 'topToolbar'):
            self.topToolbar.setIconSize(QSize(self.top_toolbar_icon_size, self.top_toolbar_icon_size))
            if self.is_dark_theme:
                top_toolbar_style = f"""
                    QToolBar {{
                        spacing: 10px;
                        padding: 4px;
                    }}
                    QToolButton {{
                        min-width: 100px;
                        max-width: 140px;
                        min-height: 54px;
                        padding: 4px 2px;
                        margin: 1px;
                        font-size: {self.top_toolbar_font_size}px;
                        color: #e8eaed;
                        background: transparent;
                        border: none;
                        text-align: center;
                        white-space: nowrap;
                    }}
                    QToolButton:hover {{
                        color: #40c4ff;
                    }}
                """
            else:
                top_toolbar_style = f"""
                    QToolBar {{
                        spacing: 10px;
                        padding: 4px;
                    }}
                    QToolButton {{
                        min-width: 100px;
                        max-width: 140px;
                        min-height: 54px;
                        padding: 4px 2px;
                        margin: 1px;
                        font-size: {self.top_toolbar_font_size}px;
                        color: #2c3e50;
                        background: transparent;
                        border: none;
                        text-align: center;
                        white-space: nowrap;
                    }}
                    QToolButton:hover {{
                        color: #1976d2;
                    }}
                """
            self.topToolbar.setStyleSheet(top_toolbar_style)

        # Update left toolbar button styling
        if hasattr(self, 'toolbarWidget'):
            for button in self.toolButtons:
                button.setIconSize(QSize(self.left_toolbar_icon_size, self.left_toolbar_icon_size))
            if self.is_dark_theme:
                left_toolbar_style = f"""
                    QWidget {{
                        background: transparent;
                    }}
                    QToolButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #23273a, stop:1 #181b24);
                        border: 1px solid #23273a;
                        color:rgb(170, 170, 167);
                        padding: 2px;
                        margin: 1px;
                        border-radius: 6px;
                        font-weight: 600;
                        font-size: {self.left_toolbar_font_size}px;
                        min-width: 120px;
                        max-width: 160px;
                        min-height: 40px;
                        text-align: center;
                        white-space: normal;
                    }}
                    QToolButton:hover {{
                        background: #40c4ff;
                        color: #181b24;
                        border: 1.5px solid #40c4ff;
                    }}
                    QToolButton:pressed, QToolButton:checked {{
                        background: #1976d2;
                        color: #fff;
                        border: 1.5px solid #1976d2;
                    }}
                    /* Style for horizontal orientation */
                    QDockWidget[orientation="horizontal"] QWidget {{
                        background: transparent;
                    }}
                    QDockWidget[orientation="horizontal"] QVBoxLayout {{
                        flex-direction: row;
                        flex-wrap: wrap;
                        justify-content: flex-start;
                        align-items: center;
                    }}
                    QDockWidget[orientation="horizontal"] QToolButton {{
                        min-width: 120px;
                        min-height: 40px;
                        margin: 1px;
                        padding: 2px;
                    }}
                """
            else:
                left_toolbar_style = f"""
                    QWidget {{
                        background: transparent;
                    }}
                    QToolButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ffffff, stop:1 #f8f9fa);
                        border: 1px solid #e1e4e8;
                        color: #2c3e50;
                        padding: 2px;
                        margin: 1px;
                        border-radius: 6px;
                        font-weight: 600;
                        font-size: {self.left_toolbar_font_size}px;
                        min-width: 120px;
                        max-width: 160px;
                        min-height: 40px;
                        text-align: center;
                        white-space: normal;
                    }}
                    QToolButton:hover {{
                        background: #1976d2;
                        color: #ffffff;
                        border: 1.5px solid #1976d2;
                    }}
                    QToolButton:pressed, QToolButton:checked {{
                        background: #1565c0;
                        color: #ffffff;
                        border: 1.5px solid #1565c0;
                    }}
                    /* Style for horizontal orientation */
                    QDockWidget[orientation="horizontal"] QWidget {{
                        background: transparent;
                    }}
                    QDockWidget[orientation="horizontal"] QVBoxLayout {{
                        flex-direction: row;
                        flex-wrap: wrap;
                        justify-content: flex-start;
                        align-items: center;
                    }}
                    QDockWidget[orientation="horizontal"] QToolButton {{
                        min-width: 120px;
                        min-height: 40px;
                        margin: 1px;
                        padding: 2px;
                    }}
                """
            self.toolbarWidget.setStyleSheet(left_toolbar_style)

    def increase_font_size(self):
        """Increase font size for all widgets"""
        if self.toolbar_font_size < 20:  # Set maximum size
            self.toolbar_font_size += 1
            self.text_font_size += 1
            self.update_font_sizes()
            # Update welcome page zoom
            for dock_widget in self.findChildren(QtWidgets.QDockWidget):
                if dock_widget.windowTitle().startswith('Welcome'):
                    welcome_widget = dock_widget.widget()
                    if welcome_widget:
                        welcome_layout = welcome_widget.findChild(QtWidgets.QWidget)
                        if welcome_layout and hasattr(welcome_layout, 'increase_font_size'):
                            welcome_layout.increase_font_size()
            self.obj_appconfig.print_info("Font size increased")

    def decrease_font_size(self):
        """Decrease font size for all widgets"""
        if self.toolbar_font_size > 8:  # Set minimum size
            self.toolbar_font_size -= 1
            self.text_font_size -= 1
            self.update_font_sizes()
            # Update welcome page zoom
            for dock_widget in self.findChildren(QtWidgets.QDockWidget):
                if dock_widget.windowTitle().startswith('Welcome'):
                    welcome_widget = dock_widget.widget()
                    if welcome_widget:
                        welcome_layout = welcome_widget.findChild(QtWidgets.QWidget)
                        if welcome_layout and hasattr(welcome_layout, 'decrease_font_size'):
                            welcome_layout.decrease_font_size()
            self.obj_appconfig.print_info("Font size decreased")

    def reset_font_size(self):
        """Reset font sizes to default"""
        self.toolbar_font_size = 10
        self.text_font_size = 10
        self.update_font_sizes()
        # Reset welcome page zoom
        for dock_widget in self.findChildren(QtWidgets.QDockWidget):
            if dock_widget.windowTitle().startswith('Welcome'):
                welcome_widget = dock_widget.widget()
                if welcome_widget:
                    welcome_layout = welcome_widget.findChild(QtWidgets.QWidget)
                    if welcome_layout and hasattr(welcome_layout, 'reset_font_size'):
                        welcome_layout.reset_font_size()
        self.obj_appconfig.print_info("Font size reset to default")

    def handle_simulation_output(self):
        """Handle simulation standard output"""
        output = self.simulation_process.readAllStandardOutput().data().decode()
        self.obj_Mainview.update_console(output)

    def handle_simulation_error(self):
        """Handle simulation error output"""
        error = self.simulation_process.readAllStandardError().data().decode()
        self.obj_Mainview.update_console(error, is_error=True)

    def handle_simulation_finished(self, exit_code, exit_status):
        """Handle simulation completion"""
        if exit_code == 0:
            self.obj_Mainview.update_console("Simulation completed successfully!")
        else:
            self.obj_Mainview.update_console("Simulation failed!", is_error=True)
        self.simulationEndSignal.emit(exit_status, exit_code)

    def start_simulation(self, args):
        """Start simulation with given arguments"""
        self.obj_Mainview.update_console("Starting simulation...")
        self.simulation_process.start('ngspice', args)

    def cancel_simulation(self):
        """Cancel ongoing simulation"""
        if self.simulation_process.state() == QtCore.QProcess.Running:
            self.simulation_process.kill()
            self.obj_Mainview.update_console("Simulation cancelled!", is_error=True)

    def initToolBar(self):
        """
        This function initializes Tool Bars.
        It setups the icons, short-cuts and defining functonality for:

            - Top-tool-bar (New project, Open project, Close project, \
                Mode switch, Help option)
            - Left-tool-bar (Open Schematic, Convert KiCad to Ngspice, \
                Simuation, Model Editor, Subcircuit, NGHDL, Modelica \
                Converter, OM Optimisation)
        """
        # Top Tool bar
        self.newproj = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/newProject.png'),
            'New Project', self
        )
        self.newproj.setShortcut('Ctrl+N')
        self.newproj.setToolTip('New Project (Ctrl+N)')
        self.newproj.triggered.connect(self.new_project)

        self.openproj = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/openProject.png'),
            'Open Project', self
        )
        self.openproj.setShortcut('Ctrl+O')
        self.openproj.setToolTip('Open Project (Ctrl+O)')
        self.openproj.triggered.connect(self.open_project)

        self.closeproj = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/closeProject.png'),
            'Close Project', self
        )
        self.closeproj.setShortcut('Ctrl+X')
        self.closeproj.setToolTip('Close Project (Ctrl+X)')
        self.closeproj.triggered.connect(self.close_project)

        self.wrkspce = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/workspace.ico'),
            'Change Workspace', self
        )
        self.wrkspce.setShortcut('Ctrl+W')
        self.wrkspce.setToolTip('Change Workspace (Ctrl+W)')
        self.wrkspce.triggered.connect(self.change_workspace)

        
        # Theme toggle button - set initial icon for dark mode since we're in light mode
        self.theme_toggle = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/dark_mode.png'),
            'Switch Theme', self
        )
        self.theme_toggle.setShortcut('Ctrl+T')
        self.theme_toggle.setToolTip('Switch to Dark Mode (Ctrl+T)')
        self.theme_toggle.triggered.connect(self.toggle_theme)
        self.helpfile = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/helpProject.png'),
            'Help', self
        )
        self.helpfile.setShortcut('Ctrl+H')
        self.helpfile.setToolTip('Help (Ctrl+H)')
        self.helpfile.triggered.connect(self.help_project)

        # added devDocs logo and called functions
        self.devdocs = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/dev_docs.png'),
            'Dev Docs', self
        )
        self.devdocs.setShortcut('Ctrl+D')
        self.devdocs.setToolTip('Developer Documentation (Ctrl+D)')
        self.devdocs.triggered.connect(self.dev_docs)

        self.topToolbar = self.addToolBar('Top Tool Bar')
        self.topToolbar.addAction(self.newproj)
        self.topToolbar.addAction(self.openproj)
        self.topToolbar.addAction(self.closeproj)
        self.topToolbar.addAction(self.wrkspce)
        
        self.topToolbar.addAction(self.devdocs)
        self.topToolbar.addAction(self.theme_toggle)
        self.topToolbar.addAction(self.helpfile)
        self.topToolbar.setIconSize(QSize(24, 24))
        self.topToolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        
        # Add specific styling for top toolbar with theme-specific tooltip styles
        if self.is_dark_theme:
            self.topToolbar.setStyleSheet("""
                QToolBar {
                    spacing: 10px;
                    padding: 4px;
                }
                QToolButton {
                    min-width: 100px;
                    max-width: 140px;
                    min-height: 54px;
                    padding: 4px 2px;
                    margin: 1px;
                    font-size: 10.5px;
                    color: #e8eaed;
                    background: transparent;
                    border: none;
                    text-align: center;
                    white-space: nowrap;
                }
                QToolButton:hover {
                    color: #40c4ff;
                    background: rgba(64, 196, 255, 0.1);
                    border-radius: 6px;
                }
                QToolTip {
                    background-color: #23273a;
                    color: #e8eaed;
                    border: 2px solid #40c4ff;
                    padding: 12px 16px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    opacity: 255;
                    margin: 2px;
                    box-shadow: 0 4px 12px rgba(64, 196, 255, 0.4);
                }
            """)
        else:
            self.topToolbar.setStyleSheet("""
                QToolBar {
                    spacing: 10px;
                    padding: 4px;
                }
                QToolButton {
                    min-width: 100px;
                    max-width: 140px;
                    min-height: 54px;
                    padding: 4px 2px;
                    margin: 1px;
                    font-size: 10.5px;
                    color: #2c3e50;
                    background: transparent;
                    border: none;
                    text-align: center;
                    white-space: nowrap;
                }
                QToolButton:hover {
                    color: #1976d2;
                    background: rgba(25, 118, 210, 0.1);
                    border-radius: 6px;
                }
                QToolTip {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border: 2px solid #1976d2;
                    padding: 12px 16px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    opacity: 255;
                    margin: 2px;
                    box-shadow: 0 4px 12px rgba(25, 118, 210, 0.4);
                }
            """)

        # This part is setting fossee logo to the right
        self.spacer = QtWidgets.QWidget()
        self.spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        self.topToolbar.addWidget(self.spacer)
        
        self.logo = QtWidgets.QLabel()
        self.logopic = QtGui.QPixmap(
            os.path.join(
                os.path.abspath(''), init_path + 'images', 'fosseeLogo.png'
            ))
        self.logopic = self.logopic.scaled(
            QSize(150, 150), QtCore.Qt.KeepAspectRatio)
        self.logo.setPixmap(self.logopic)
        self.logo.setStyleSheet("padding:0 15px 0 0;")
        self.topToolbar.addWidget(self.logo)

        # Adding Action Widget to tool bar
        self.kicad = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/kicad.png'),
            'Open Schematic', self
        )
        self.kicad.setShortcut('Ctrl+K')  # Shortcut for Open Schematic
        self.kicad.setToolTip('Open Schematic (Ctrl+K)')
        self.kicad.triggered.connect(self.obj_kicad.openSchematic)

        self.conversion = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/ki-ng.png'),
            'Convert KiCad to Ngspice', self
        )
        self.conversion.setShortcut('Ctrl+G')  # Shortcut for Convert KiCad to Ngspice
        self.conversion.setToolTip('Convert KiCad to Ngspice (Ctrl+G)')
        self.conversion.triggered.connect(self.obj_kicad.openKicadToNgspice)

        self.ngspice = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/ngspice.png'),
            'Simulate', self
        )
        self.ngspice.setShortcut('Ctrl+M')  # Shortcut for Simulate
        self.ngspice.setToolTip('Simulate (Ctrl+M)')
        self.ngspice.triggered.connect(self.plotFlagPopBox)

        self.model = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/model.png'),
            'Model Editor', self
        )
        self.model.setShortcut('Ctrl+E')  # Shortcut for Model Editor
        self.model.setToolTip('Model Editor (Ctrl+E)')
        self.model.triggered.connect(self.open_modelEditor)

        self.subcircuit = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/subckt.png'),
            'Subcircuit', self
        )
        self.subcircuit.setShortcut('Ctrl+B')  # Shortcut for Subcircuit
        self.subcircuit.setToolTip('Subcircuit (Ctrl+B)')
        self.subcircuit.triggered.connect(self.open_subcircuit)

        self.nghdl = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/nghdl.png'), 'NGHDL', self
        )
        self.nghdl.setShortcut('Ctrl+H')  # Shortcut for NGHDL
        self.nghdl.setToolTip('NGHDL (Ctrl+H)')
        self.nghdl.triggered.connect(self.open_nghdl)

        self.makerchip = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/makerchip.png'),
            'Makerchip-NgVeri', self
        )
        self.makerchip.setShortcut('Ctrl+V')  # Shortcut for Makerchip-NgVeri
        self.makerchip.setToolTip('Makerchip-NgVeri (Ctrl+V)')
        self.makerchip.triggered.connect(self.open_makerchip)

        self.omedit = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/omedit.png'),
            'Modelica Converter', self
        )
        self.omedit.setShortcut('Ctrl+I')  # Shortcut for Modelica Converter
        self.omedit.setToolTip('Modelica Converter (Ctrl+I)')
        self.omedit.triggered.connect(self.open_OMedit)

        self.omoptim = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/omoptim.png'),
            'OM Optimisation', self
        )
        self.omoptim.setShortcut('Ctrl+Y')  # Shortcut for OM Optimisation
        self.omoptim.setToolTip('OM Optimisation (Ctrl+Y)')
        self.omoptim.triggered.connect(self.open_OMoptim)

        self.conToeSim = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/icon.png'),
            'Schematics converter', self
        )
        self.conToeSim.setShortcut('Ctrl+J')  # Shortcut for Schematics converter
        self.conToeSim.setToolTip('Schematics converter (Ctrl+J)')
        self.conToeSim.triggered.connect(self.open_conToeSim)

        # Create a scrollable left toolbar
        # Create a dock widget for the left toolbar
        self.leftDock = QtWidgets.QDockWidget("Tools", self)
        self.leftDock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        self.leftDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        
        # Create scroll area
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        
        # Create widget to hold toolbar buttons
        self.toolbarWidget = QtWidgets.QWidget()
        self.toolbarLayout = QtWidgets.QVBoxLayout(self.toolbarWidget)
        self.toolbarLayout.setSpacing(8)
        self.toolbarLayout.setContentsMargins(8, 8, 8, 8)
        
        # Create tool buttons and add them to the layout
        self.toolButtons = []
        
        # Helper function to create tool buttons
        def createToolButton(action, iconSize=QSize(24, 24)):
            button = QtWidgets.QToolButton()
            button.setDefaultAction(action)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            button.setIconSize(iconSize)
            button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            button.setMinimumWidth(120)  # Increased width
            button.setMinimumHeight(40)  # Reduced height
            button.setMaximumWidth(160)  # Increased max width
            return button
        
        # Create buttons for each action
        actions = [
            self.kicad, self.conversion, self.ngspice, self.model,
            self.subcircuit, self.makerchip, self.nghdl, self.omedit,
            self.omoptim, self.conToeSim
        ]
        
        for action in actions:
            button = createToolButton(action)
            self.toolButtons.append(button)
            self.toolbarLayout.addWidget(button)
        
        # Add stretch to push buttons to top
        self.toolbarLayout.addStretch()
        
        # Set the widget to scroll area
        self.scrollArea.setWidget(self.toolbarWidget)
        
        # Set scroll area to dock widget
        self.leftDock.setWidget(self.scrollArea)
        
        # Add dock widget to main window
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.leftDock)
        
        # Apply enhanced styling for the scrollable toolbar
        self.leftDock.setStyleSheet("""
            QDockWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #23273a;
                border-radius: 14px;
                font-weight: 600;
            }
            QDockWidget::title {
                text-align: center;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #23273a, stop:1 #181b24);
                color: #40c4ff;
                border-radius: 14px 14px 0 0;
                padding: 8px 12px;
                font-weight: 700;
                font-size: 14px;
                letter-spacing: 0.5px;
                border-bottom: 1px solid #23273a;
            }
            QDockWidget::close-button, QDockWidget::float-button {
                background: transparent;
                border: none;
                color: #40c4ff;
                padding: 4px;
            }
            QDockWidget::close-button:hover, QDockWidget::float-button:hover {
                background: #40c4ff;
                color: #181b24;
                border-radius: 4px;
            }
        """)
        
        self.toolbarWidget.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                border: 1px solid #23273a;
                color:rgb(170, 170, 167);
                padding: 2px;
                margin: 1px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 120px;
                max-width: 160px;
                min-height: 40px;
                text-align: center;
                white-space: normal;
            }
            QToolButton:hover {
                background: #40c4ff;
                color: #181b24;
                border: 1.5px solid #40c4ff;
            }
            QToolButton:pressed, QToolButton:checked {
                background: #1976d2;
                color: #fff;
                border: 1.5px solid #1976d2;
            }
            /* Style for horizontal orientation */
            QDockWidget[orientation="horizontal"] QWidget {{
                background: transparent;
            }}
            QDockWidget[orientation="horizontal"] QVBoxLayout {{
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: flex-start;
                align-items: center;
            }}
            QDockWidget[orientation="horizontal"] QToolButton {{
                min-width: 120px;
                min-height: 40px;
                margin: 1px;
                padding: 2px;
            }}
        """)

        # Apply initial toolbar button styling with current font sizes
        self.update_toolbar_button_styling()

    def apply_dark_theme(self):
        """Applies a premium, modern dark theme everywhere using only supported QSS properties."""
        premium_dark_stylesheet = """
        QMainWindow, QDialog, QMessageBox {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0e1a, stop:0.3 #1a1d29, stop:0.7 #1e2124, stop:1 #0f1419);
            color: #e8eaed;
            font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 12px;
            font-weight: 500;
        }
        QWidget {
            background: transparent;
            color: #e8eaed;
        }
        QWidget#centralWidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0e1a, stop:0.3 #1a1d29, stop:0.7 #1e2124, stop:1 #0f1419);
        }
        QMessageBox {
            background-color: #23273a;
            color: #e8eaed;
            border: 1px solid #181b24;
            border-radius: 8px;
        }
        QMessageBox QLabel {
            color: #e8eaed;
            background: transparent;
        }
        QErrorMessage {
            background-color: #23273a;
            color: #e8eaed;
            border: 1px solid #181b24;
            border-radius: 8px;
        }
        QErrorMessage QTextEdit {
            background-color: #23273a;
            color: #e8eaed;
            border: 1px solid #181b24;
            border-radius: 8px;
            padding: 8px;
        }
        QDockWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #e8eaed;
            border: 1px solid #23273a;
            border-radius: 14px;
        }
        QDockWidget > QWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: none;
            border-radius: 8px;
        }
        QDockWidget::title {
            text-align: left;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #23273a, stop:1 #181b24);
            color: #40c4ff;
            border-radius: 14px 14px 0 0;
            padding: 8px 12px;
            font-weight: 700;
            font-size: 13px;
            min-width: 200px;
            max-width: none;
            border-bottom: 1px solid #23273a;
        }
        QGroupBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: 1px solid #23273a;
            border-radius: 14px;
            margin-top: 24px;
            color: #e8eaed;
            font-weight: 600;
            padding-top: 16px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 8px 16px 4px 16px;
            color: #40c4ff;
            background: transparent;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.5px;
        }
        QToolBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: 1px solid #23273a;
            border-radius: 8px;
            color: #e8eaed;
            padding: 4px 8px;
            spacing: 4px;
            margin: 2px;
        }
        QToolBar::separator {
            background: #23273a;
            width: 1px;
            margin: 4px 6px;
        }
        QToolButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: 1px solid #23273a;
            color: #ffffff;
            padding: 4px;
            margin: 2px;
            border-radius: 6px;
            font-weight: 600;
            letter-spacing: 0.3px;
            min-width: 120px;
            max-width: 160px;
        }
        QToolButton:hover {
            background: #1976d2;
            color: #ffffff;
            border: 1.5px solid #1976d2;
        }
        QToolButton:pressed, QToolButton:checked {
            background: #1976d2;
            color: #fff;
            border: 1.5px solid #1976d2;
        }
        QLabel {
            color: #e8eaed;
            font-weight: 500;
            font-size: 13px;
            letter-spacing: 0.2px;
        }
        QMenuBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: none;
            border-bottom: 1px solid #23273a;
            color: #e8eaed;
            font-weight: 600;
        }
        QMenuBar::item {
            background: transparent;
            color: #e8eaed;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 2px;
            font-weight: 600;
        }
        QMenuBar::item:selected {
            background: #23273a;
            color: #40c4ff;
        }
        QMenu {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #e8eaed;
            border: 1px solid #23273a;
            border-radius: 12px;
            padding: 8px;
        }
        QMenu::item {
            padding: 10px 24px;
            border-radius: 8px;
            margin: 2px;
            font-weight: 600;
        }
        QMenu::item:selected {
            background: #40c4ff;
            color: #181b24;
        }
        QMenu::separator {
            height: 1px;
            background: #23273a;
            margin: 8px 16px;
        }
        QTreeWidget, QTreeView, QListView {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #e8eaed;
            border: 1px solid #23273a;
            border-radius: 12px;
            selection-background-color: #40c4ff;
            selection-color: #181b24;
            font-weight: 600;
            padding: 4px;
        }
        QTreeView::item:hover, QListView::item:hover {
            background: #23273a;
            color: #40c4ff;
        }
        QTreeView::item:selected, QListView::item:selected {
            background: #40c4ff;
            color: #181b24;
            font-weight: 700;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #23273a, stop:1 #181b24);
            color: #40c4ff;
            font-weight: 700;
            font-size: 17px;
            border: none;
            border-radius: 0;
            padding: 12px 0px 12px 18px;
            letter-spacing: 0.5px;
        }
        QTreeView::branch {
            background: transparent;
            width: 16px;
        }
        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {
            image: url(images/branch-closed.png);
        }
        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {
            image: url(images/branch-open.png);
        }
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #b0b3b8;
            border: 1px solid #23273a;
            border-bottom: none;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            padding: 12px 28px;
            margin-right: 4px;
            font-weight: 600;
            font-size: 13px;
            letter-spacing: 0.3px;
        }
        QTabBar::tab:selected {
            background: #40c4ff;
            color: #181b24;
            border: 1px solid #40c4ff;
            border-bottom: 3px solid #40c4ff;
            font-weight: 700;
        }
        QTabBar::tab:hover:!selected {
            background: #23273a;
            color: #e8eaed;
        }
        QTabWidget::pane {
            border: 1px solid #23273a;
            border-radius: 0 12px 12px 12px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
        }
        QTextEdit, QLineEdit, QPlainTextEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #e8eaed;
            border: 1px solid #23273a;
            border-radius: 10px;
            padding: 12px 16px;
            font-weight: 500;
            font-size: 13px;
            selection-background-color: #40c4ff;
            selection-color: #181b24;
        }
        QTextEdit:focus, QLineEdit:focus, QPlainTextEdit:focus {
            border: 2px solid #40c4ff;
            background: #181b24;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #40c4ff, stop:1 #1976d2);
            color: #181b24;
            border: 1px solid #40c4ff;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.5px;
        }
        QPushButton:hover {
            background: #1976d2;
            color: #fff;
            border: 1.5px solid #1976d2;
        }
        QPushButton:pressed {
            background: #23273a;
            color: #40c4ff;
            border: 1.5px solid #40c4ff;
        }
        QPushButton:disabled {
            background: #23273a;
            color: #888;
            border: 1px solid #23273a;
        }
        QStatusBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #23273a, stop:1 #181b24);
            color: #b0b3b8;
            border: none;
            border-top: 1px solid #23273a;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.3px;
        }
        QScrollBar:vertical, QScrollBar:horizontal {
            background: #23273a;
            border-radius: 6px;
            margin: 0;
        }
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: #40c4ff;
            border-radius: 6px;
            min-height: 30px;
            min-width: 30px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
            background: #1976d2;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            background: none;
            border: none;
        }
        QProgressBar {
            background: #23273a;
            border: 1px solid #23273a;
            border-radius: 8px;
            text-align: center;
            color: #e8eaed;
            font-weight: 600;
        }
        QProgressBar::chunk {
            background: #40c4ff;
            border-radius: 7px;
        }
        QComboBox {
            background: #23273a;
            border: 1px solid #23273a;
            border-radius: 10px;
            padding: 8px 16px;
            color: #e8eaed;
            font-weight: 600;
        }
        QComboBox:hover {
            border: 1.5px solid #40c4ff;
            background: #181b24;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid #40c4ff;
            margin-right: 12px;
        }
        QSplitter::handle {
            background: #23273a;
            border-radius: 2px;
        }
        QSplitter::handle:hover {
            background: #40c4ff;
        }
        QHeaderView::section:horizontal {
            min-height: 36px;
        }
        QToolTip {
            background: #23273a;
            color: #e8eaed;
            border: 1px solid #40c4ff;
            border-radius: 8px;
            padding: 8px 12px;
            font-weight: 600;
            font-size: 12px;
        }
        """
        self.setStyleSheet(premium_dark_stylesheet)
        
        # Update all dock widgets and their children
        for dock_widget in self.findChildren(QtWidgets.QDockWidget):
            dock_widget.setStyleSheet(premium_dark_stylesheet)
            for child in dock_widget.findChildren(QtWidgets.QWidget):
                if isinstance(child, (QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit)):
                    child.setStyleSheet("""
                        QTextEdit, QPlainTextEdit {
                            background: #23273a;
                            color: #e8eaed;
                            border: 1px solid #181b24;
                            border-radius: 8px;
                            selection-background-color: #40c4ff;
                            selection-color: #181b24;
                        }
                    """)
                elif isinstance(child, QtWidgets.QLineEdit):
                    child.setStyleSheet("""
                        QLineEdit {
                            background: #23273a;
                            color: #e8eaed;
                            border: 1px solid #181b24;
                            border-radius: 8px;
                            selection-background-color: #40c4ff;
                            selection-color: #181b24;
                        }
                    """)
                else:
                    child.setStyleSheet(premium_dark_stylesheet)
        
        # Update project explorer theme
        if hasattr(self.obj_Mainview, 'obj_projectExplorer'):
            self.obj_Mainview.obj_projectExplorer.apply_dark_theme()
        
        # Update welcome message theme
        self.obj_Mainview.apply_dark_theme_welcome()

    def apply_light_theme(self):
        """Apply light theme to the application."""
        premium_light_stylesheet = """
        QMainWindow, QDialog, QMessageBox {
            background: #ffffff;
            color: #2c3e50;
            font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 12px;
            font-weight: 500;
        }
        QWidget {
            background: transparent;
            color: #2c3e50;
        }
        QWidget#centralWidget {
            background: #ffffff;
        }
        QMessageBox {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
        }
        QMessageBox QLabel {
            color: #2c3e50;
            background: transparent;
        }
        QErrorMessage {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
        }
        QErrorMessage QTextEdit {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
        }
        QDockWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 14px;
        }
        QDockWidget > QWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: none;
            border-radius: 8px;
        }
        QDockWidget::title {
            text-align: left;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #1976d2;
            border-radius: 14px 14px 0 0;
            padding: 8px 12px;
            font-weight: 700;
            font-size: 13px;
            min-width: 200px;
            max-width: none;
            border-bottom: 1px solid #e1e4e8;
        }
        QGroupBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: 1px solid #e1e4e8;
            border-radius: 14px;
            margin-top: 24px;
            color: #2c3e50;
            font-weight: 600;
            padding-top: 16px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 8px 16px 4px 16px;
            color: #1976d2;
            background: transparent;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.5px;
        }
        QToolBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: none;
            border-bottom: 1px solid #e1e4e8;
        }
        QToolBar::separator {
            background: #e1e4e8;
            width: 1px;
            margin: 4px 6px;
        }
        QToolButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: 1px solid #e1e4e8;
            color: #2c3e50;
            padding: 4px;
            margin: 2px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 9px;
            letter-spacing: 0.3px;
            min-width: 120px;
            max-width: 160px;
        }
        QToolButton:hover {
            background: #1976d2;
            color: #ffffff;
            border: 1.5px solid #1976d2;
        }
        QToolButton:pressed, QToolButton:checked {
            background: #1565c0;
            color: #ffffff;
            border: 1.5px solid #1565c0;
        }
        QLabel {
            color: #2c3e50;
            font-weight: 500;
            font-size: 13px;
            letter-spacing: 0.2px;
        }
        QMenuBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: none;
            border-bottom: 1px solid #e1e4e8;
            color: #2c3e50;
            font-weight: 600;
        }
        QMenuBar::item {
            background: transparent;
            color: #2c3e50;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 2px;
            font-weight: 600;
        }
        QMenuBar::item:selected {
            background: #f1f4f9;
            color: #1976d2;
        }
        QMenu {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 12px;
            padding: 8px;
        }
        QMenu::item {
            padding: 10px 24px;
            border-radius: 8px;
            margin: 2px;
            font-weight: 600;
        }
        QMenu::item:selected {
            background: #1976d2;
            color: #ffffff;
        }
        QMenu::separator {
            height: 1px;
            background: #e1e4e8;
            margin: 8px 16px;
        }
        QTreeWidget, QTreeView, QListView {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 12px;
            selection-background-color: #1976d2;
            selection-color: #ffffff;
            font-weight: 600;
            padding: 4px;
        }
        QTreeView::item:hover, QListView::item:hover {
            background: #f1f4f9;
            color: #1976d2;
        }
        QTreeView::item:selected, QListView::item:selected {
            background: #1976d2;
            color: #ffffff;
            font-weight: 700;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #1976d2;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
            font-weight: 600;
        }
        QScrollBar:vertical {
            background: #f8f9fa;
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #c1c9d6;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #1976d2;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background: #f8f9fa;
            height: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #c1c9d6;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #1976d2;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QTabWidget::pane {
            border: 1px solid #e1e4e8;
            border-radius: 0 12px 12px 12px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
        }
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 8px 16px;
            margin-right: 2px;
            font-weight: 600;
        }
        QTabBar::tab:selected {
            background: #1976d2;
            color: #ffffff;
            border: 1px solid #1976d2;
        }
        QTabBar::tab:hover:!selected {
            background: #f1f4f9;
            color: #1976d2;
        }
        QTextEdit, QLineEdit, QPlainTextEdit {
            background: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
            selection-background-color: #1976d2;
            selection-color: #ffffff;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #1976d2;
            color: #ffffff;
            border: 1.5px solid #1976d2;
        }
        QPushButton:pressed {
            background: #1565c0;
            color: #ffffff;
            border: 1.5px solid #1565c0;
        }
        QComboBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
            min-width: 6em;
        }
        QComboBox:hover {
            border: 1.5px solid #1976d2;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: url(images/down_arrow.png);
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            selection-background-color: #1976d2;
            selection-color: #ffffff;
        }
        QCheckBox {
            color: #2c3e50;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
            background: #ffffff;
        }
        QCheckBox::indicator:checked {
            background: #1976d2;
            border: 1px solid #1976d2;
        }
        QCheckBox::indicator:hover {
            border: 1.5px solid #1976d2;
        }
        QRadioButton {
            color: #2c3e50;
            spacing: 8px;
        }
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #e1e4e8;
            border-radius: 9px;
            background: #ffffff;
        }
        QRadioButton::indicator:checked {
            background: #1976d2;
            border: 1px solid #1976d2;
        }
        QRadioButton::indicator:hover {
            border: 1.5px solid #1976d2;
        }
        QSpinBox, QDoubleSpinBox {
            background: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
        }
        QSpinBox:hover, QDoubleSpinBox:hover {
            border: 1.5px solid #1976d2;
        }
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            background: #f8f9fa;
            border: none;
            border-radius: 4px;
            width: 16px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
            background: #1976d2;
        }
        QSpinBox::up-arrow, QSpinBox::down-arrow,
        QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
            width: 8px;
            height: 8px;
            background: #2c3e50;
        }
        QProgressBar {
            background: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            text-align: center;
            color: #2c3e50;
        }
        QProgressBar::chunk {
            background: #1976d2;
            border-radius: 8px;
        }
        QSlider::groove:horizontal {
            background: #f8f9fa;
            height: 4px;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #1976d2;
            border: none;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        QSlider::handle:horizontal:hover {
            background: #1565c0;
        }
        QSlider::groove:vertical {
            background: #f8f9fa;
            width: 4px;
            border-radius: 2px;
        }
        QSlider::handle:vertical {
            background: #1976d2;
            border: none;
            width: 16px;
            height: 16px;
            margin: 0 -6px;
            border-radius: 8px;
        }
        QSlider::handle:vertical:hover {
            background: #1565c0;
        }
        QStatusBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border-top: 1px solid #e1e4e8;
        }
        QStatusBar::item {
            border: none;
        }
        QStatusBar QLabel {
            color: #2c3e50;
        }
        QToolTip {
            background: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
        }
        """
        
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
            }
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: none;
                border-bottom: 1px solid #e1e4e8;
            }
            QToolBar QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #e1e4e8;
                color: #000000;
                padding: 4px;
                margin: 2px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 9px;
                letter-spacing: 0.3px;
                min-width: 120px;
                max-width: 160px;
                min-height: 40px;
                text-align: center;
            }
            QToolBar QToolButton:hover {
                background: #1976d2;
                color: #ffffff;
                border: 1.5px solid #1976d2;
            }
        """)
        
        # Update all dock widgets and their children
        for dock_widget in self.findChildren(QtWidgets.QDockWidget):
            dock_widget.setStyleSheet(premium_light_stylesheet)
            for child in dock_widget.findChildren(QtWidgets.QWidget):
                if isinstance(child, (QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit)):
                    child.setStyleSheet("""
                        QTextEdit, QPlainTextEdit {
                            background: #ffffff;
                            color: #2c3e50;
                            border: 1px solid #e1e4e8;
                            border-radius: 8px;
                            selection-background-color: #1976d2;
                            selection-color: #ffffff;
                        }
                    """)
                elif isinstance(child, QtWidgets.QLineEdit):
                    child.setStyleSheet("""
                        QLineEdit {
                            background: #ffffff;
                            color: #2c3e50;
                            border: 1px solid #e1e4e8;
                            border-radius: 8px;
                            selection-background-color: #1976d2;
                            selection-color: #ffffff;
                        }
                    """)
                else:
                    child.setStyleSheet(premium_light_stylesheet)
        
        # Update project explorer theme
        if hasattr(self.obj_Mainview, 'obj_projectExplorer'):
            self.obj_Mainview.obj_projectExplorer.apply_light_theme()
        
        # Update welcome message theme
        self.obj_Mainview.apply_light_theme_welcome()

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.apply_dark_theme()

            self.theme_toggle.setIcon(QtGui.QIcon(init_path + 'images/sun.png'))
            self.theme_toggle.setToolTip('Switch to Light Mode (Ctrl+T)')

            # Update schematic converter theme
            self.update_schematic_converter_theme(is_dark=True)
            # Update model editor theme
            self.update_model_editor_theme(is_dark=True)
            # Update makerchip-ngveri theme
            self.update_makerchip_ngveri_theme(is_dark=True)
            # Update simulation TerminalUi theme
            if hasattr(self, 'current_terminalui_widget') and self.current_terminalui_widget is not None:
                self.current_terminalui_widget.set_theme(True)
        else:
            self.apply_light_theme()
            self.theme_toggle.setIcon(QtGui.QIcon(init_path + 'images/dark_mode.png'))
            self.theme_toggle.setToolTip('Switch to Dark Mode (Ctrl+T)')
            # Update schematic converter theme
            self.update_schematic_converter_theme(is_dark=False)
            # Update model editor theme
            self.update_model_editor_theme(is_dark=False)
            # Update makerchip-ngveri theme
            self.update_makerchip_ngveri_theme(is_dark=False)
            # Update simulation TerminalUi theme
            if hasattr(self, 'current_terminalui_widget') and self.current_terminalui_widget is not None:
                self.current_terminalui_widget.set_theme(False)

        # Update Project Explorer theme
        self.obj_Mainview.obj_projectExplorer.set_theme(self.is_dark_theme)
        
        # Update all dock widgets and their children
        for dock_widget in self.findChildren(QtWidgets.QDockWidget):
            if self.is_dark_theme:
                self.apply_dark_theme_to_widget(dock_widget)
            else:
                self.apply_light_theme_to_widget(dock_widget)
            # Update all children of the dock widget
            for child in dock_widget.findChildren(QtWidgets.QWidget):
                if self.is_dark_theme:
                    self.apply_dark_theme_to_widget(child)
                else:
                    self.apply_light_theme_to_widget(child)

        # Update toolbar button styling to maintain font sizes
        self.update_toolbar_button_styling()

        # Force update of the UI
        self.repaint()

    def update_schematic_converter_theme(self, is_dark):
        """Update schematic converter theme based on current theme."""
        if is_dark:
            # Dark theme for schematic converter
            converter_style = """
                QGroupBox {{
                    border: 2px solid #40c4ff;
                    border-radius: 14px;
                    margin-top: 1em;
                    padding: 15px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #23273a, stop:1 #181b24);
                    color: #e8eaed;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px;
                    color: #40c4ff;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QLineEdit {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #23273a, stop:1 #181b24);
                    color: #e8eaed;
                    border: 2px solid #40c4ff;
                    border-radius: 10px;
                    padding: 8px 15px;
                    font-weight: 500;
                    font-size: 12px;
                }}
                QLineEdit:focus {{
                    border: 2px solid #1976d2;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2a2f3a, stop:1 #1e2128);
                    /* box-shadow: 0 0 10px rgba(64, 196, 255, 0.3); */
                }}
                QLineEdit::placeholder {{
                    color: #b0b3b8;
                    font-style: italic;
                }}
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #40c4ff, stop:1 #1976d2);
                    color: #181b24;
                    border: 1px solid #40c4ff;
                    border-radius: 10px;
                    padding: 10px 20px;
                    font-weight: 700;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: #1976d2;
                    color: #fff;
                    border: 1.5px solid #1976d2;
                }}
                QPushButton:pressed {{
                    background: #23273a;
                    color: #40c4ff;
                    border: 1.5px solid #40c4ff;
                }}
                QLabel {{
                    color: #e8eaed;
                }}
            """
            # Dark theme description styling
            description_style = """
                body {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #23273a, stop:1 #181b24);
                    color: #e8eaed;
                    border: 2px solid #40c4ff;
                }}
                h1 {{
                    color: #40c4ff;
                    border-bottom: 2px solid #40c4ff;
                }}
                b {{
                    color: #40c4ff;
                }}
            """
        else:
            # Light theme for schematic converter
            converter_style = """
                QGroupBox {{
                    border: 2px solid #1976d2;
                    border-radius: 14px;
                    margin-top: 1em;
                    padding: 15px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f8f9fa);
                    color: #2c3e50;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px;
                    color: #1976d2;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QLineEdit {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f8f9fa);
                    color: #2c3e50;
                    border: 2px solid #1976d2;
                    border-radius: 10px;
                    padding: 8px 15px;
                    font-weight: 500;
                    font-size: 12px;
                }}
                QLineEdit:focus {{
                    border: 2px solid #1565c0;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f9fa, stop:1 #ffffff);
                    /* box-shadow: 0 0 10px rgba(25, 118, 210, 0.3); */
                }}
                QLineEdit::placeholder {{
                    color: #7f8c8d;
                    font-style: italic;
                }}
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1976d2, stop:1 #1565c0);
                    color: #ffffff;
                    border: 1px solid #1976d2;
                    border-radius: 10px;
                    padding: 10px 20px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #1565c0;
                    color: #fff;
                    border: 1.5px solid #1565c0;
                }
                QPushButton:pressed {
                    background: #0d47a1;
                    color: #ffffff;
                    border: 1.5px solid #0d47a1;
                }
                QLabel {
                    color: #2c3e50;
                }
            """
            # Light theme description styling
            description_style = """
                body {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f8f9fa);
                    color: #2c3e50;
                    border: 2px solid #1976d2;
                }
                h1 {
                    color: #1976d2;
                    border-bottom: 2px solid #1976d2;
                }
                b {
                    color: #1976d2;
                }
            """

        # Apply styles to schematic converter widgets
        try:
            # Find schematic converter widgets and apply theme
            for widget in self.findChildren(QtWidgets.QWidget):
                if hasattr(widget, 'objectName') and widget.objectName() == 'schematic_converter':
                    widget.setStyleSheet(converter_style)
                # Also apply to any QTextBrowser widgets that might contain descriptions
                if isinstance(widget, QtWidgets.QTextBrowser):
                    widget.document().setDefaultStyleSheet(description_style)
        except Exception as e:
            print(f"Error updating schematic converter theme: {e}")

    def update_model_editor_theme(self, is_dark):
        """Update model editor theme based on current theme and update the widget if open."""
        if is_dark:
            # Dark theme for model editor
            model_editor_style = """
                QGroupBox {
                    border: 2px solid #40c4ff;
                    border-radius: 14px;
                    margin-top: 1em;
                    padding: 15px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #23273a, stop:1 #181b24);
                    color: #e8eaed;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px;
                    color: #40c4ff;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #40c4ff, stop:1 #1976d2);
                    color: #181b24;
                    border: 1px solid #40c4ff;
                    min-height: 35px;
                    min-width: 120px;
                    padding: 8px 15px;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #1976d2;
                    color: #fff;
                    border: 1.5px solid #1976d2;
                }
                QPushButton:pressed {
                    background: #23273a;
                    color: #40c4ff;
                    border: 1.5px solid #40c4ff;
                }
                QPushButton:disabled {
                    background: #23273a;
                    color: #888;
                    border: 1px solid #23273a;
                }
                QRadioButton {
                    color: #e8eaed;
                    font-weight: 600;
                    font-size: 13px;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                    border: 2px solid #40c4ff;
                    border-radius: 8px;
                    background: #23273a;
                }
                QRadioButton::indicator:checked {
                    background: #40c4ff;
                    border: 2px solid #40c4ff;
                }
                QComboBox {
                    background: #23273a;
                    color: #e8eaed;
                    border: 1px solid #40c4ff;
                    border-radius: 8px;
                    padding: 5px 10px;
                    min-height: 30px;
                    font-size: 12px;
                }
                QComboBox:hover {
                    border: 1.5px solid #1976d2;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    width: 12px;
                    height: 12px;
                }
                QTableWidget {
                    background: #23273a;
                    color: #e8eaed;
                    border: 1px solid #40c4ff;
                    border-radius: 8px;
                    gridline-color: #40c4ff;
                    font-size: 12px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #181b24;
                }
                QTableWidget::item:selected {
                    background: #40c4ff;
                    color: #181b24;
                }
                QHeaderView::section {
                    background: #181b24;
                    color: #40c4ff;
                    border: 1px solid #40c4ff;
                    padding: 8px;
                    font-weight: 700;
                }
                QLabel {
                    color: #e8eaed;
                }
            """
        else:
            # Light theme for model editor
            model_editor_style = """
            
            #    QWidget { background: transparent; }
            #    QPushButton {
            #        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8f9fa, stop:1 #e9ecef);
            #        color: #1976d2;
            #        border: 1px solid #1976d2;
            #        min-height: 35px;
            #        min-width: 120px;
            #        padding: 8px 15px;
            #        border-radius: 10px;
            #        font-weight: 700;
            #        font-size: 12px;
            #    }
            #    QPushButton:hover {
            #        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e3f2fd, stop:1 #bbdefb);
            #        color: #1565c0;
            #        border: 1px solid #1565c0;
            #    }
            #    QPushButton:pressed {
            #        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1976d2, stop:1 #1565c0);
            #        color: #ffffff;
            #        border: 1px solid #1565c0;
            #    }
            #    QPushButton:disabled {
            #        background: #f5f5f5;
            #        color: #9e9e9e;
            #        border: 1px solid #e0e0e0;
            #    }
            #    QRadioButton { color: #2c3e50; font-weight: 600; font-size: 13px; }
            #    QRadioButton::indicator { width: 16px; height: 16px; border: 2px solid #1976d2; border-radius: 8px; background: #ffffff; }
            #    QRadioButton::indicator:checked { background: #1976d2; border: 2px solid #1976d2; }
            #    QComboBox { background: #ffffff; color: #2c3e50; border: 1px solid #1976d2; border-radius: 8px; padding: 5px 10px; min-height: 30px; font-size: 12px; }
            #    QComboBox:hover { border: 1.5px solid #1565c0; }
            #    QComboBox::drop-down { border: none; width: 20px; }
            #    QComboBox::down-arrow { width: 12px; height: 12px; }
            #    QTableWidget { background: #ffffff; color: #2c3e50; border: 1px solid #1976d2; border-radius: 8px; gridline-color: #1976d2; font-size: 12px; }
            #    QTableWidget::item { padding: 8px; border-bottom: 1px solid #f8f9fa; }
            #    QTableWidget::item:selected { background: #1976d2; color: #ffffff; }
            #    QHeaderView::section { background: #f8f9fa; color: #1976d2; border: 1px solid #1976d2; padding: 8px; font-weight: 700; }
            #    QLabel { color: #2c3e50; }
        
            """

        # Apply styles to model editor widgets
        try:
            # Find model editor widgets and apply theme
            for widget in self.findChildren(QtWidgets.QWidget):
                if hasattr(widget, 'objectName') and 'model' in widget.objectName().lower():
                    widget.setStyleSheet(model_editor_style)
                # Also apply to any ModelEditorclass instances
                if hasattr(widget, '__class__') and 'ModelEditorclass' in str(widget.__class__):
                    widget.setStyleSheet(model_editor_style)
            # --- NEW: update the actual model editor widget if present ---
            if hasattr(self, 'current_modeleditor_widget') and self.current_modeleditor_widget is not None:
                self.current_modeleditor_widget.set_theme(is_dark)
        except Exception as e:
            print(f"Error updating model editor theme: {e}")

    def update_makerchip_ngveri_theme(self, is_dark):
        """Update makerchip-ngveri theme based on current theme and update the widget if open."""
        if is_dark:
            # Dark theme for makerchip-ngveri
            makerchip_style = """
                QGroupBox {
                    border: 2px solid #40c4ff;
                    border-radius: 14px;
                    margin-top: 1em;
                    padding: 15px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #23273a, stop:1 #181b24);
                    color: #e8eaed;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px;
                    color: #40c4ff;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #40c4ff, stop:1 #1976d2);
                    color: #181b24;
                    border: 1px solid #40c4ff;
                    min-height: 35px;
                    min-width: 120px;
                    padding: 8px 15px;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #1976d2;
                    color: #fff;
                    border: 1.5px solid #1976d2;
                }
                QPushButton:pressed {
                    background: #23273a;
                    color: #40c4ff;
                    border: 1.5px solid #40c4ff;
                }
                QPushButton:disabled {
                    background: #23273a;
                    color: #888;
                    border: 1px solid #23273a;
                }
                QTextEdit {
                    background: #23273a;
                    color: #e8eaed;
                    border: 1px solid #40c4ff;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 12px;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
                QComboBox {
                    background: #23273a;
                    color: #e8eaed;
                    border: 1px solid #40c4ff;
                    border-radius: 8px;
                    padding: 5px 10px;
                    min-height: 30px;
                    font-size: 12px;
                }
                QComboBox:hover {
                    border: 1.5px solid #1976d2;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    width: 12px;
                    height: 12px;
                }
                QLineEdit {
                    background: #23273a;
                    color: #e8eaed;
                    border: 1px solid #40c4ff;
                    border-radius: 8px;
                    padding: 8px 12px;
                    min-height: 30px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 1.5px solid #1976d2;
                }
                QLabel {
                    color: #e8eaed;
                }
                QTabWidget::pane {
                    border: 1px solid #40c4ff;
                    border-radius: 8px;
                    background: #23273a;
                }
                QTabBar::tab {
                    background: #181b24;
                    color: #e8eaed;
                    padding: 8px 16px;
                    border: 1px solid #40c4ff;
                    border-bottom: none;
                    border-radius: 8px 8px 0 0;
                    font-weight: 600;
                }
                QTabBar::tab:selected {
                    background: #40c4ff;
                    color: #181b24;
                }
                QTabBar::tab:hover {
                    background: #1976d2;
                    color: #ffffff;
                }
            """
        else:
            # Light theme for makerchip-ngveri
            makerchip_style = """
                QGroupBox {
                    border: 2px solid #1976d2;
                    border-radius: 14px;
                    margin-top: 1em;
                    padding: 15px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f8f9fa);
                    color: #2c3e50;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px;
                    color: #1976d2;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1976d2, stop:1 #1565c0);
                    color: #ffffff;
                    border: 1px solid #1976d2;
                    min-height: 35px;
                    min-width: 120px;
                    padding: 8px 15px;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #1565c0;
                    color: #fff;
                    border: 1.5px solid #1565c0;
                }
                QPushButton:pressed {
                    background: #0d47a1;
                    color: #ffffff;
                    border: 1.5px solid #0d47a1;
                }
                QPushButton:disabled {
                    background: #e1e4e8;
                    color: #7f8c8d;
                    border: 1px solid #e1e4e8;
                }
                QTextEdit {
                    background: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #1976d2;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 12px;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
                QComboBox {
                    background: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #1976d2;
                    border-radius: 8px;
                    padding: 5px 10px;
                    min-height: 30px;
                    font-size: 12px;
                }
                QComboBox:hover {
                    border: 1.5px solid #1565c0;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    width: 12px;
                    height: 12px;
                }
                QLineEdit {
                    background: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #1976d2;
                    border-radius: 8px;
                    padding: 8px 12px;
                    min-height: 30px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 1.5px solid #1565c0;
                }
                QLabel {
                    color: #2c3e50;
                }
                QTabWidget::pane {
                    border: 1px solid #1976d2;
                    border-radius: 8px;
                    background: #ffffff;
                }
                QTabBar::tab {
                    background: #f8f9fa;
                    color: #2c3e50;
                    padding: 8px 16px;
                    border: 1px solid #1976d2;
                    border-bottom: none;
                    border-radius: 8px 8px 0 0;
                    font-weight: 600;
                }
                QTabBar::tab:selected {
                    background: #1976d2;
                    color: #ffffff;
                }
                QTabBar::tab:hover {
                    background: #1565c0;
                    color: #ffffff;
                }
            """

        # Apply styles to makerchip-ngveri widgets
        try:
            # Find makerchip-ngveri widgets and apply theme
            for widget in self.findChildren(QtWidgets.QWidget):
                if hasattr(widget, 'objectName') and ('makerchip' in widget.objectName().lower() or 'ngveri' in widget.objectName().lower()):
                    widget.setStyleSheet(makerchip_style)
                # Also apply to any Maker or NgVeri class instances
                if hasattr(widget, '__class__') and ('Maker' in str(widget.__class__) or 'NgVeri' in str(widget.__class__)):
                    widget.setStyleSheet(makerchip_style)
            # --- NEW: update the actual makerchip widget if present ---
            if hasattr(self, 'current_makerchip_widget') and self.current_makerchip_widget is not None:
                self.current_makerchip_widget.set_theme(is_dark)
        except Exception as e:
            print(f"Error updating makerchip-ngveri theme: {e}")

    def plotFlagPopBox(self):
        """This function displays a pop-up box with message- Do you want Ngspice plots? and oprions Yes and NO.
        
        If the user clicks on Yes, both the NgSpice and python plots are displayed and if No is clicked then only the python plots."""

        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Ngspice Plots")
        msg_box.setText("Do you want Ngspice plots?")
        
        yes_button = msg_box.addButton("Yes", QtWidgets.QMessageBox.YesRole)
        no_button = msg_box.addButton("No", QtWidgets.QMessageBox.NoRole)

        msg_box.exec_()

        if msg_box.clickedButton() == yes_button:
            self.plotFlag = True  
        else:
            self.plotFlag = False  

        self.open_ngspice()

    def closeEvent(self, event):
        '''
        This function closes the ongoing program (process).
        When exit button is pressed a Message box pops out with \
        exit message and buttons 'Yes', 'No'.

            1. If 'Yes' is pressed:
                - check that program (process) in procThread_list \
                  (a list made in Appconfig.py):

                    - if available it terminates that program.
                    - if the program (process) is not available, \
                      then check it in process_obj (a list made in \
                      Appconfig.py) and if found, it closes the program.

            2. If 'No' is pressed:
                - the program just continues as it was doing earlier.
        '''
        exit_msg = "Are you sure you want to exit the program?"
        exit_msg += " All unsaved data will be lost."
        reply = QtWidgets.QMessageBox.question(
            self, 'Message', exit_msg, QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            for proc in self.obj_appconfig.procThread_list:
                try:
                    proc.terminate()
                except BaseException:
                    pass
            try:
                for process_object in self.obj_appconfig.process_obj:
                    try:
                        process_object.close()
                    except BaseException:
                        pass
            except BaseException:
                pass

            # Check if "Open project" and "New project" window is open.
            # If yes, just close it when application is closed.
            try:
                self.project.close()
            except BaseException:
                pass
            event.accept()
            self.systemTrayIcon.showMessage('Exit', 'eSim is Closed.')

        elif reply == QtWidgets.QMessageBox.No:
            event.ignore()

    def new_project(self):
        """This function call New Project Info class."""
        text, ok = QtWidgets.QInputDialog.getText(
            self, 'New Project Info', 'Enter Project Name:'
        )
        updated = False

        if ok:
            self.projname = (str(text))
            self.project = NewProjectInfo()
            directory, filelist = self.project.createProject(self.projname)

            if directory and filelist:
                self.obj_Mainview.obj_projectExplorer.addTreeNode(
                    directory, filelist
                )
                updated = True

        if not updated:
            print("No new project created")
            self.obj_appconfig.print_info('No new project created')
            try:
                self.obj_appconfig.print_info(
                    'Current project is : ' +
                    self.obj_appconfig.current_project["ProjectName"]
                )
            except BaseException:
                pass

    def open_project(self):
        """This project call Open Project Info class."""
        print("Function : Open Project")
        self.project = OpenProjectInfo()
        try:
            directory, filelist = self.project.body()
            self.obj_Mainview.obj_projectExplorer.addTreeNode(
                directory, filelist)
        except BaseException:
            pass

    def close_project(self):
        """
        This function closes the saved project.
        It first checks whether project (file) is present in list.

            - If present:
                - it first kills that process-id.
                - closes that file.
                - Shows message "Current project <path_to_file> is closed"

            - If not present: pass
        """
        print("Function : Close Project")
        current_project = self.obj_appconfig.current_project['ProjectName']
        if current_project is None:
            pass
        else:
            temp = self.obj_appconfig.current_project['ProjectName']
            for pid in self.obj_appconfig.proc_dict[temp]:
                try:
                    os.kill(pid, 9)
                except BaseException:
                    pass
            self.obj_Mainview.obj_dockarea.closeDock()
            self.obj_appconfig.current_project['ProjectName'] = None
            self.systemTrayIcon.showMessage(
                'Close', 'Current project ' +
                os.path.basename(current_project) + ' is Closed.'
            )

    def change_workspace(self):
        """This function opens a dialog to choose the workspace."""
        self.obj_workspace.changeWorkspace()

    def help_project(self):
        """This function opens help documentation."""
        print("Function : Help")
        self.obj_appconfig.print_info('Help is called')
        print("Current Project is : ", self.obj_appconfig.current_project)
        self.obj_Mainview.obj_dockarea.usermanual(self.is_dark_theme)

    def dev_docs(self):
        """
        This function guides the user to readthedocs website for the developer docs
        """
        print("Function : DevDocs")
        self.obj_appconfig.print_info('DevDocs is called')
        print("Current Project is : ", self.obj_appconfig.current_project)
        webbrowser.open("https://esim.readthedocs.io/en/latest/index.html")

    @QtCore.pyqtSlot(QtCore.QProcess.ExitStatus, int)
    def plotSimulationData(self, exitCode, exitStatus):
        """Enables interaction for new simulation and
           displays the plotter dock where graphs can be plotted.
        """
        self.ngspice.setEnabled(True)
        self.conversion.setEnabled(True)
        self.closeproj.setEnabled(True)
        self.wrkspce.setEnabled(True)

        if exitStatus == QtCore.QProcess.NormalExit and exitCode == 0:
            try:
                self.obj_Mainview.obj_dockarea.plottingEditor()
            except Exception as e:
                self.msg = QtWidgets.QErrorMessage()
                self.msg.setModal(True)
                self.msg.setWindowTitle("Error Message")
                self.msg.showMessage(
                    'Data could not be plotted. Please try again.'
                )
                self.msg.exec_()
                print("Exception Message:", str(e), traceback.format_exc())
                self.obj_appconfig.print_error('Exception Message : '
                                               + str(e))

    def open_ngspice(self):
        """This Function execute ngspice on current project."""
        projDir = self.obj_appconfig.current_project["ProjectName"]

        if projDir is not None:
            projName = os.path.basename(projDir)
            ngspiceNetlist = os.path.join(projDir, projName + ".cir.out")

            if not os.path.isfile(ngspiceNetlist):
                print(
                    "Netlist file (*.cir.out) not found."
                )
                self.msg = QtWidgets.QErrorMessage()
                self.msg.setModal(True)
                self.msg.setWindowTitle("Error Message")
                self.msg.showMessage(
                    'Netlist (*.cir.out) not found.'
                )
                self.msg.exec_()
                return

            # --- Store reference to the TerminalUi widget for theme updates ---
            self.obj_Mainview.obj_dockarea.ngspiceEditor(
                projName, ngspiceNetlist, self.simulationEndSignal, self.plotFlag)
            # Find the most recently created NgspiceWidget and its TerminalUi
            try:
                ngspice_widget = self.obj_Mainview.obj_dockarea.ngspiceLayout.itemAt(0).widget()
                if hasattr(ngspice_widget, 'terminalUi'):
                    self.current_terminalui_widget = ngspice_widget.terminalUi
            except Exception as e:
                self.current_terminalui_widget = None

            self.ngspice.setEnabled(False)
            self.conversion.setEnabled(False)
            self.closeproj.setEnabled(False)
            self.wrkspce.setEnabled(False)

        else:
            self.msg = QtWidgets.QErrorMessage()
            self.msg.setModal(True)
            self.msg.setWindowTitle("Error Message")
            self.msg.showMessage(
                'Please select the project first.'
                ' You can either create new project or open existing project'
            )
            self.msg.exec_()

    def open_subcircuit(self):
        """
        This function opens 'subcircuit' option in left-tool-bar.
        When 'subcircuit' icon is clicked wich is present in
        left-tool-bar of main page:

            - Meassge shown on screen "Subcircuit editor is called".
            - 'subcircuiteditor()' function is called using object
              'obj_dockarea' of class 'Mainview'.
        """
        print("Function : Subcircuit editor")
        self.obj_appconfig.print_info('Subcircuit editor is called')
        self.obj_Mainview.obj_dockarea.subcircuiteditor()

    def open_nghdl(self):
        """
        This function calls NGHDL option in left-tool-bar.
        It uses validateTool() method from Validation.py:

            - If 'nghdl' is present in executables list then
              it passes command 'nghdl -e' to WorkerThread class of
              Worker.py.
            - If 'nghdl' is not present, then it shows error message.
        """
        print("Function : NGHDL")
        self.obj_appconfig.print_info('NGHDL is called')

        if self.obj_validation.validateTool('nghdl'):
            self.cmd = 'nghdl -e'
            self.obj_workThread = Worker.WorkerThread(self.cmd)
            self.obj_workThread.start()
        else:
            self.msg = QtWidgets.QErrorMessage()
            self.msg.setModal(True)
            self.msg.setWindowTitle('NGHDL Error')
            self.msg.showMessage('Error while opening NGHDL. ' +
                                 'Please make sure it is installed')
            self.obj_appconfig.print_error('Error while opening NGHDL. ' +
                                           'Please make sure it is installed')
            self.msg.exec_()

    def open_makerchip(self):
        """
        This function opens 'subcircuit' option in left-tool-bar.
        When 'subcircuit' icon is clicked wich is present in
        left-tool-bar of main page:

            - Meassge shown on screen "Subcircuit editor is called".
            - 'subcircuiteditor()' function is called using object
              'obj_dockarea' of class 'Mainview'.
        """
        print("Function : Makerchip and Verilator to Ngspice Converter")
        self.obj_appconfig.print_info('Makerchip is called')
        self.obj_Mainview.obj_dockarea.makerchip()
        # --- Store reference to the currently open makerchip widget ---
        if hasattr(self.obj_Mainview.obj_dockarea, 'makerchip_instance'):
            self.current_makerchip_widget = self.obj_Mainview.obj_dockarea.makerchip_instance
        else:
            self.current_makerchip_widget = None

    def open_modelEditor(self):
        """
        This function opens model editor option in left-tool-bar.
        When model editor icon is clicked which is present in
        left-tool-bar of main page:

            - Meassge shown on screen "Model editor is called".
            - 'modeleditor()' function is called using object
              'obj_dockarea' of class 'Mainview'.
        """
        print("Function : Model editor")
        self.obj_appconfig.print_info('Model editor is called')
        self.obj_Mainview.obj_dockarea.modelEditor()
        # --- Store reference to the currently open model editor widget ---
        if hasattr(self.obj_Mainview.obj_dockarea, 'modeleditor_instance'):
            self.current_modeleditor_widget = self.obj_Mainview.obj_dockarea.modeleditor_instance
        else:
            self.current_modeleditor_widget = None

    def open_OMedit(self):
        """
        This function calls ngspice to OMEdit converter and then launch OMEdit.
        """
        self.obj_appconfig.print_info('OMEdit is called')
        self.projDir = self.obj_appconfig.current_project["ProjectName"]

        if self.projDir is not None:
            if self.obj_validation.validateCirOut(self.projDir):
                self.projName = os.path.basename(self.projDir)
                self.ngspiceNetlist = os.path.join(
                    self.projDir, self.projName + ".cir.out"
                )
                self.modelicaNetlist = os.path.join(
                    self.projDir, self.projName + ".mo"
                )

                """
                try:
                    # Creating a command for Ngspice to Modelica converter
                    self.cmd1 = "
                        python3 ../ngspicetoModelica/NgspicetoModelica.py "\
                            + self.ngspiceNetlist
                    self.obj_workThread1 = Worker.WorkerThread(self.cmd1)
                    self.obj_workThread1.start()
                    if self.obj_validation.validateTool("OMEdit"):
                        # Creating command to run OMEdit
                        self.cmd2 = "OMEdit "+self.modelicaNetlist
                        self.obj_workThread2 = Worker.WorkerThread(self.cmd2)
                        self.obj_workThread2.start()
                    else:
                        self.msg = QtWidgets.QMessageBox()
                        self.msgContent = "There was an error while
                            opening OMEdit.<br/>\
                        Please make sure OpenModelica is installed in your\
                            system. <br/>\
                        To install it on Linux : Go to\
                            <a href=https://www.openmodelica.org/download/\
                                download-linux>OpenModelica Linux</a> and  \
                                    install nigthly build release.<br/>\
                        To install it on Windows : Go to\
                         <a href=https://www.openmodelica.org/download/\
                        download-windows>OpenModelica Windows</a>\
                         and install latest version.<br/>"
                        self.msg.setTextFormat(QtCore.Qt.RichText)
                        self.msg.setText(self.msgContent)
                        self.msg.setWindowTitle("Missing OpenModelica")
                        self.obj_appconfig.print_info(self.msgContent)
                        self.msg.exec_()

                except Exception as e:
                    self.msg = QtWidgets.QErrorMessage()
                    self.msg.setModal(True)
                    self.msg.setWindowTitle(
                        "Ngspice to Modelica conversion error")
                    self.msg.showMessage(
                        'Unable to convert NgSpice netlist to\
                            Modelica netlist :'+str(e))
                    self.msg.exec_()
                    self.obj_appconfig.print_error(str(e))
                """

                self.obj_Mainview.obj_dockarea.modelicaEditor(self.projDir)

            else:
                self.msg = QtWidgets.QErrorMessage()
                self.msg.setModal(True)
                self.msg.setWindowTitle("Missing Ngspice Netlist")
                self.msg.showMessage(
                    'Current project does not contain any Ngspice file. ' +
                    'Please create Ngspice file with extension .cir.out'
                )
                self.msg.exec_()
        else:
            self.msg = QtWidgets.QErrorMessage()
            self.msg.setModal(True)
            self.msg.setWindowTitle("Error Message")
            self.msg.showMessage(
                'Please select the project first. You can either ' +
                'create a new project or open an existing project'
            )
            self.msg.exec_()

    def open_OMoptim(self):
        """
        This function uses validateTool() method from Validation.py:

            - If 'OMOptim' is present in executables list then
              it passes command 'OMOptim' to WorkerThread class of Worker.py
            - If 'OMOptim' is not present, then it shows error message with
              link to download it on Linux and Windows.
        """
        print("Function : OMOptim")
        self.obj_appconfig.print_info('OMOptim is called')
        # Check if OMOptim is installed
        if self.obj_validation.validateTool("OMOptim"):
            # Creating a command to run
            self.cmd = "OMOptim"
            self.obj_workThread = Worker.WorkerThread(self.cmd)
            self.obj_workThread.start()
        else:
            self.msg = QtWidgets.QMessageBox()
            self.msgContent = (
                "There was an error while opening OMOptim.<br/>"
                "Please make sure OpenModelica is installed in your"
                " system.<br/>"
                "To install it on Linux : Go to <a href="
                "https://www.openmodelica.org/download/download-linux"
                ">OpenModelica Linux</a> and install nightly build"
                " release.<br/>"
                "To install it on Windows : Go to <a href="
                "https://www.openmodelica.org/download/download-windows"
                ">OpenModelica Windows</a> and install latest version.<br/>"
            )
            self.msg.setTextFormat(QtCore.Qt.RichText)
            self.msg.setText(self.msgContent)
            self.msg.setWindowTitle("Error Message")
            self.obj_appconfig.print_info(self.msgContent)
            self.msg.exec_()

    def open_conToeSim(self):
        print("Function : Schematics converter")
        self.obj_appconfig.print_info('Schematics converter is called')
        self.obj_Mainview.obj_dockarea.eSimConverter()

    def apply_dark_theme_to_widget(self, widget):
        """Apply the dark theme stylesheet to a specific widget."""
        premium_dark_stylesheet = """
        QMainWindow, QDialog, QMessageBox {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0e1a, stop:0.3 #1a1d29, stop:0.7 #1e2124, stop:1 #0f1419);
            color: #e8eaed;
            font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 12px;
            font-weight: 500;
        }
        QWidget {
            background: transparent;
            color: #e8eaed;
        }
        QWidget#centralWidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0e1a, stop:0.3 #1a1d29, stop:0.7 #1e2124, stop:1 #0f1419);
        }
        QMessageBox {
            background-color: #23273a;
            color: #e8eaed;
            border: 1px solid #181b24;
            border-radius: 8px;
        }
        QMessageBox QLabel {
            color: #e8eaed;
            background: transparent;
        }
        QErrorMessage {
            background-color: #23273a;
            color: #e8eaed;
            border: 1px solid #181b24;
            border-radius: 8px;
        }
        QErrorMessage QTextEdit {
            background-color: #23273a;
            color: #e8eaed;
            border: 1px solid #181b24;
            border-radius: 8px;
            padding: 8px;
        }
        QDockWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #e8eaed;
            border: 1px solid #23273a;
            border-radius: 14px;
        }
        QDockWidget > QWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: none;
            border-radius: 8px;
        }
        QDockWidget::title {
            text-align: left;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #23273a, stop:1 #181b24);
            color: #40c4ff;
            border-radius: 14px 14px 0 0;
            padding: 8px 12px;
            font-weight: 700;
            font-size: 13px;
            min-width: 200px;
            max-width: none;
            border-bottom: 1px solid #23273a;
        }
        QGroupBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: 1px solid #23273a;
            border-radius: 14px;
            margin-top: 24px;
            color: #e8eaed;
            font-weight: 600;
            padding-top: 16px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 8px 16px 4px 16px;
            color: #40c4ff;
            background: transparent;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.5px;
        }
        QToolBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: 1px solid #23273a;
            border-radius: 8px;
            color: #e8eaed;
            padding: 4px 8px;
            spacing: 4px;
            margin: 2px;
        }
        QToolBar::separator {
            background: #23273a;
            width: 1px;
            margin: 4px 6px;
        }
        QToolButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: 1px solid #23273a;
            color: #ffffff;
            padding: 4px;
            margin: 2px;
            border-radius: 6px;
            font-weight: 600;
            letter-spacing: 0.3px;
            min-width: 120px;
            max-width: 160px;
        }
        QToolButton:hover {
            background: #1976d2;
            color: #ffffff;
            border: 1.5px solid #1976d2;
        }
        QToolButton:pressed, QToolButton:checked {
            background: #1976d2;
            color: #fff;
            border: 1.5px solid #1976d2;
        }
        QLabel {
            color: #e8eaed;
            font-weight: 500;
            font-size: 13px;
            letter-spacing: 0.2px;
        }
        QMenuBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            border: none;
            border-bottom: 1px solid #23273a;
            color: #e8eaed;
            font-weight: 600;
        }
        QMenuBar::item {
            background: transparent;
            color: #e8eaed;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 2px;
            font-weight: 600;
        }
        QMenuBar::item:selected {
            background: #23273a;
            color: #40c4ff;
        }
        QMenu {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #e8eaed;
            border: 1px solid #23273a;
            border-radius: 12px;
            padding: 8px;
        }
        QMenu::item {
            padding: 10px 24px;
            border-radius: 8px;
            margin: 2px;
            font-weight: 600;
        }
        QMenu::item:selected {
            background: #40c4ff;
            color: #181b24;
        }
        QMenu::separator {
            height: 1px;
            background: #23273a;
            margin: 8px 16px;
        }
        QTreeWidget, QTreeView, QListView {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #e8eaed;
            border: 1px solid #23273a;
            border-radius: 12px;
            selection-background-color: #40c4ff;
            selection-color: #181b24;
            font-weight: 600;
            padding: 4px;
        }
        QTreeView::item:hover, QListView::item:hover {
            background: #23273a;
            color: #40c4ff;
        }
        QTreeView::item:selected, QListView::item:selected {
            background: #40c4ff;
            color: #181b24;
            font-weight: 700;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #23273a, stop:1 #181b24);
            color: #40c4ff;
            font-weight: 700;
            font-size: 17px;
            border: none;
            border-radius: 0;
            padding: 12px 0px 12px 18px;
            letter-spacing: 0.5px;
        }
        QTreeView::branch {
            background: transparent;
            width: 16px;
        }
        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {
            image: url(images/branch-closed.png);
        }
        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {
            image: url(images/branch-open.png);
        }
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #b0b3b8;
            border: 1px solid #23273a;
            border-bottom: none;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            padding: 12px 28px;
            margin-right: 4px;
            font-weight: 600;
            font-size: 13px;
            letter-spacing: 0.3px;
        }
        QTabBar::tab:selected {
            background: #40c4ff;
            color: #181b24;
            border: 1px solid #40c4ff;
            border-bottom: 3px solid #40c4ff;
            font-weight: 700;
        }
        QTabBar::tab:hover:!selected {
            background: #23273a;
            color: #e8eaed;
        }
        QTabWidget::pane {
            border: 1px solid #23273a;
            border-radius: 0 12px 12px 12px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
        }
        QTextEdit, QLineEdit, QPlainTextEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #23273a, stop:1 #181b24);
            color: #e8eaed;
            border: 1px solid #23273a;
            border-radius: 10px;
            padding: 12px 16px;
            font-weight: 500;
            font-size: 13px;
            selection-background-color: #40c4ff;
            selection-color: #181b24;
        }
        QTextEdit:focus, QLineEdit:focus, QPlainTextEdit:focus {
            border: 2px solid #40c4ff;
            background: #181b24;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #40c4ff, stop:1 #1976d2);
            color: #181b24;
            border: 1px solid #40c4ff;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.5px;
        }
        QPushButton:hover {
            background: #1976d2;
            color: #fff;
            border: 1.5px solid #1976d2;
        }
        QPushButton:pressed {
            background: #23273a;
            color: #40c4ff;
            border: 1.5px solid #40c4ff;
        }
        QPushButton:disabled {
            background: #23273a;
            color: #888;
            border: 1px solid #23273a;
        }
        QStatusBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #23273a, stop:1 #181b24);
            color: #b0b3b8;
            border: none;
            border-top: 1px solid #23273a;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.3px;
        }
        QScrollBar:vertical, QScrollBar:horizontal {
            background: #23273a;
            border-radius: 6px;
            margin: 0;
        }
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: #40c4ff;
            border-radius: 6px;
            min-height: 30px;
            min-width: 30px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
            background: #1976d2;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            background: none;
            border: none;
        }
        QProgressBar {
            background: #23273a;
            border: 1px solid #23273a;
            border-radius: 8px;
            text-align: center;
            color: #e8eaed;
            font-weight: 600;
        }
        QProgressBar::chunk {
            background: #40c4ff;
            border-radius: 7px;
        }
        QComboBox {
            background: #23273a;
            border: 1px solid #23273a;
            border-radius: 10px;
            padding: 8px 16px;
            color: #e8eaed;
            font-weight: 600;
        }
        QComboBox:hover {
            border: 1.5px solid #40c4ff;
            background: #181b24;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid #40c4ff;
            margin-right: 12px;
        }
        QSplitter::handle {
            background: #23273a;
            border-radius: 2px;
        }
        QSplitter::handle:hover {
            background: #40c4ff;
        }
        QHeaderView::section:horizontal {
            min-height: 36px;
        }
        QToolTip {
            background: #23273a;
            color: #e8eaed;
            border: 1px solid #40c4ff;
            border-radius: 8px;
            padding: 8px 12px;
            font-weight: 600;
            font-size: 12px;
        }
        """
        widget.setStyleSheet(premium_dark_stylesheet)

    def apply_light_theme_to_widget(self, widget):
        """Apply the light theme stylesheet to a specific widget."""
        premium_light_stylesheet = """
        QMainWindow, QDialog, QMessageBox {
            background: #ffffff;
            color: #2c3e50;
            font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 12px;
            font-weight: 500;
        }
        QWidget {
            background: transparent;
            color: #2c3e50;
        }
        QWidget#centralWidget {
            background: #ffffff;
        }
        QMessageBox {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
        }
        QMessageBox QLabel {
            color: #2c3e50;
            background: transparent;
        }
        QErrorMessage {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
        }
        QErrorMessage QTextEdit {
            background-color: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
        }
        QDockWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 14px;
        }
        QDockWidget > QWidget {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: none;
            border-radius: 8px;
        }
        QDockWidget::title {
            text-align: left;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #1976d2;
            border-radius: 14px 14px 0 0;
            padding: 8px 12px;
            font-weight: 700;
            font-size: 13px;
            min-width: 200px;
            max-width: none;
            border-bottom: 1px solid #e1e4e8;
        }
        QGroupBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: 1px solid #e1e4e8;
            border-radius: 14px;
            margin-top: 24px;
            color: #2c3e50;
            font-weight: 600;
            padding-top: 16px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 8px 16px 4px 16px;
            color: #1976d2;
            background: transparent;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.5px;
        }
        QToolBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: none;
            border-bottom: 1px solid #e1e4e8;
        }
        QToolBar::separator {
            background: #e1e4e8;
            width: 1px;
            margin: 4px 6px;
        }
        QToolButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: 1px solid #e1e4e8;
            color: #2c3e50;
            padding: 4px;
            margin: 2px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 9px;
            letter-spacing: 0.3px;
            min-width: 120px;
            max-width: 160px;
        }
        QToolButton:hover {
            background: #1976d2;
            color: #ffffff;
            border: 1.5px solid #1976d2;
        }
        QToolButton:pressed, QToolButton:checked {
            background: #1565c0;
            color: #ffffff;
            border: 1.5px solid #1565c0;
        }
        QLabel {
            color: #2c3e50;
            font-weight: 500;
            font-size: 13px;
            letter-spacing: 0.2px;
        }
        QMenuBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: none;
            border-bottom: 1px solid #e1e4e8;
            color: #2c3e50;
            font-weight: 600;
        }
        QMenuBar::item {
            background: transparent;
            color: #2c3e50;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 2px;
            font-weight: 600;
        }
        QMenuBar::item:selected {
            background: #f1f4f9;
            color: #1976d2;
        }
        QMenu {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 12px;
            padding: 8px;
        }
        QMenu::item {
            padding: 10px 24px;
            border-radius: 8px;
            margin: 2px;
            font-weight: 600;
        }
        QMenu::item:selected {
            background: #1976d2;
            color: #ffffff;
        }
        QMenu::separator {
            height: 1px;
            background: #e1e4e8;
            margin: 8px 16px;
        }
        QTreeWidget, QTreeView, QListView {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 12px;
            selection-background-color: #1976d2;
            selection-color: #ffffff;
            font-weight: 600;
            padding: 4px;
        }
        QTreeView::item:hover, QListView::item:hover {
            background: #f1f4f9;
            color: #1976d2;
        }
        QTreeView::item:selected, QListView::item:selected {
            background: #1976d2;
            color: #ffffff;
            font-weight: 700;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #1976d2;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
            font-weight: 600;
        }
        QScrollBar:vertical {
            background: #f8f9fa;
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #c1c9d6;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #1976d2;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background: #f8f9fa;
            height: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #c1c9d6;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #1976d2;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QTabWidget::pane {
            border: 1px solid #e1e4e8;
            border-radius: 0 12px 12px 12px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
        }
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 8px 16px;
            margin-right: 2px;
            font-weight: 600;
        }
        QTabBar::tab:selected {
            background: #1976d2;
            color: #ffffff;
            border: 1px solid #1976d2;
        }
        QTabBar::tab:hover:!selected {
            background: #f1f4f9;
            color: #1976d2;
        }
        QTextEdit, QLineEdit, QPlainTextEdit {
            background: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
            selection-background-color: #1976d2;
            selection-color: #ffffff;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #1976d2;
            color: #ffffff;
            border: 1.5px solid #1976d2;
        }
        QPushButton:pressed {
            background: #1565c0;
            color: #ffffff;
            border: 1.5px solid #1565c0;
        }
        QComboBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
            min-width: 6em;
        }
        QComboBox:hover {
            border: 1.5px solid #1976d2;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: url(images/down_arrow.png);
            width: 12px;
            height: 12px;
        }
        QComboBox QAbstractItemView {
            background: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            selection-background-color: #1976d2;
            selection-color: #ffffff;
        }
        QCheckBox {
            color: #2c3e50;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
            background: #ffffff;
        }
        QCheckBox::indicator:checked {
            background: #1976d2;
            border: 1px solid #1976d2;
        }
        QCheckBox::indicator:hover {
            border: 1.5px solid #1976d2;
        }
        QRadioButton {
            color: #2c3e50;
            spacing: 8px;
        }
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #e1e4e8;
            border-radius: 9px;
            background: #ffffff;
        }
        QRadioButton::indicator:checked {
            background: #1976d2;
            border: 1px solid #1976d2;
        }
        QRadioButton::indicator:hover {
            border: 1.5px solid #1976d2;
        }
        QSpinBox, QDoubleSpinBox {
            background: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
        }
        QSpinBox:hover, QDoubleSpinBox:hover {
            border: 1.5px solid #1976d2;
        }
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            background: #f8f9fa;
            border: none;
            border-radius: 4px;
            width: 16px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
            background: #1976d2;
        }
        QSpinBox::up-arrow, QSpinBox::down-arrow,
        QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
            width: 8px;
            height: 8px;
            background: #2c3e50;
        }
        QProgressBar {
            background: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            text-align: center;
            color: #2c3e50;
        }
        QProgressBar::chunk {
            background: #1976d2;
            border-radius: 8px;
        }
        QSlider::groove:horizontal {
            background: #f8f9fa;
            height: 4px;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #1976d2;
            border: none;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        QSlider::handle:horizontal:hover {
            background: #1565c0;
        }
        QSlider::groove:vertical {
            background: #f8f9fa;
            width: 4px;
            border-radius: 2px;
        }
        QSlider::handle:vertical {
            background: #1976d2;
            border: none;
            width: 16px;
            height: 16px;
            margin: 0 -6px;
            border-radius: 8px;
        }
        QSlider::handle:vertical:hover {
            background: #1565c0;
        }
        QStatusBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            color: #2c3e50;
            border-top: 1px solid #e1e4e8;
        }
        QStatusBar::item {
            border: none;
        }
        QStatusBar QLabel {
            color: #2c3e50;
        }
        QToolTip {
            background: #ffffff;
            color: #2c3e50;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
        }
        """
        widget.setStyleSheet(premium_light_stylesheet)

    def increase_toolbar_font_size(self):
        """Increase font size for toolbar buttons and icon size"""
        if self.top_toolbar_font_size < 24:
            self.top_toolbar_font_size += 1
            self.left_toolbar_font_size += 1
            self.top_toolbar_icon_size = min(self.top_toolbar_icon_size + self.toolbar_icon_step, self.top_toolbar_icon_max)
            self.left_toolbar_icon_size = min(self.left_toolbar_icon_size + self.toolbar_icon_step, self.left_toolbar_icon_max)
            self.update_font_sizes()
            self.obj_appconfig.print_info("Toolbar font and icon size increased")

    def decrease_toolbar_font_size(self):
        """Decrease font size for toolbar buttons and icon size"""
        if self.top_toolbar_font_size > 8:
            self.top_toolbar_font_size -= 1
            self.left_toolbar_font_size -= 1
            self.top_toolbar_icon_size = max(self.top_toolbar_icon_size - self.toolbar_icon_step, self.top_toolbar_icon_min)
            self.left_toolbar_icon_size = max(self.left_toolbar_icon_size - self.toolbar_icon_step, self.left_toolbar_icon_min)
            self.update_font_sizes()
            self.obj_appconfig.print_info("Toolbar font and icon size decreased")

    def reset_toolbar_font_size(self):
        """Reset font size and icon size for toolbar buttons"""
        self.top_toolbar_font_size = 10
        self.left_toolbar_font_size = 9
        self.top_toolbar_icon_size = 24
        self.left_toolbar_icon_size = 24
        self.update_font_sizes()
        self.obj_appconfig.print_info("Toolbar font and icon size reset to default")



# This class initialize the Main View of Application
class MainView(QtWidgets.QWidget):
    """
    This class defines whole view and style of main page:

        - Position of tool bars:
            - Top tool bar.
            - Left tool bar.
        - Project explorer Area.
        - Dock area.
        - Console area.
    """

    def __init__(self, is_dark_theme=False, *args):
        # call init method of superclass
        QtWidgets.QWidget.__init__(self, *args)

        # Initialize theme state
        self.is_dark_theme = is_dark_theme
        
        # Initialize appconfig
        self.obj_appconfig = Appconfig()

        # Create main layout
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.leftSplit = QtWidgets.QSplitter()
        self.middleContainer = QtWidgets.QWidget()
        self.middleContainerLayout = QtWidgets.QVBoxLayout()
        self.middleSplit = QtWidgets.QSplitter()
        
        self.noteArea = QtWidgets.QTextEdit()
        self.noteArea.setReadOnly(True)
        # Set explicit scrollbar policy
        self.noteArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.noteArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.obj_appconfig.noteArea['Note'] = self.noteArea
        self.obj_appconfig.noteArea['Note'].append(
            '        eSim Started......')
        self.obj_appconfig.noteArea['Note'].append('Project Selected : None')
        self.obj_appconfig.noteArea['Note'].append('\n')

        # Enhanced CSS with proper scrollbar styling
        self.noteArea.setStyleSheet("""
            QTextEdit {
                font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                line-height: 1.4;
                padding: 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #23273a;
                border-radius: 12px;
            }
            QScrollBar:vertical {
                background: #23273a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #40c4ff;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #1976d2;
            }
            QScrollBar:horizontal {
                background: #23273a;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #40c4ff;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #1976d2;
            }
        """)

        self.obj_dockarea = DockArea.DockArea(self.is_dark_theme)
        self.obj_projectExplorer = ProjectExplorer.ProjectExplorer(self.is_dark_theme)

        # Main horizontal layout to hold Project Explorer and DockArea
        self.layout = QtWidgets.QHBoxLayout()
        # Adding Project Explorer to the layout
        self.layout.addWidget(self.obj_projectExplorer)
        self.layout.setStretchFactor(self.obj_projectExplorer, 1)

        # Adding content to vertical middle Split
        self.middleSplit = QtWidgets.QSplitter()
        self.middleSplit.setOrientation(QtCore.Qt.Vertical)
        self.middleSplit.addWidget(self.obj_dockarea)
        self.middleSplit.addWidget(self.noteArea)

        self.layout.addWidget(self.middleSplit)
        self.layout.setStretchFactor(self.middleSplit, 3)

        self.setLayout(self.layout)
        self.show()

        self.obj_projectExplorer.projectOpened.connect(self.openProjectInTabs)

    def update_console(self, text, is_error=False):
        """Update the console area with the given text and error flag."""
        if is_error:
            self.noteArea.setStyleSheet("""
                QTextEdit {
                    font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                    line-height: 1.4;
                    padding: 16px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #23273a, stop:1 #181b24);
                    color: #e8eaed;
                    border: 1px solid #23273a;
                    border-radius: 12px;
                }
            """)
            self.noteArea.append(text)
        else:
            self.noteArea.setStyleSheet("""
                QTextEdit {
                    font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                    line-height: 1.4;
                    padding: 16px;
                    background: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #e1e4e8;
                    border-radius: 12px;
                }
            """)
            self.noteArea.append(text)

    def apply_dark_theme_welcome(self):
        """Apply dark theme to console"""
        self.is_dark_theme = True
        # Note: Font size is now handled in update_font_sizes()
        self.noteArea.setStyleSheet("""
            QTextEdit {
                font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                line-height: 1.4;
                padding: 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #23273a;
                border-radius: 12px;
            }
        """)
        self.noteArea.setStyleSheet("""
            QLabel {
                font-weight: 600;
                color: #b0bec5;
                padding: 8px 0px;
                border-bottom: 2px solid rgba(64, 196, 255, 0.3);
            }
        """)

    def apply_light_theme_welcome(self):
        """Apply light theme to console"""
        self.is_dark_theme = False
        # Note: Font size is now handled in update_font_sizes()
        self.noteArea.setStyleSheet("""
            QTextEdit {
                font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                line-height: 1.4;
                padding: 16px;
                background: #ffffff;
                color: #2c3e50;
                border: 1px solid #e1e4e8;
                border-radius: 12px;
            }
        """)
        self.noteArea.setStyleSheet("""
            QLabel {
                font-weight: 600;
                color: #2c3e50;
                padding: 8px 0px;
                border-bottom: 2px solid rgba(25, 118, 210, 0.3);
            }
        """)

    def openProjectInTabs(self, projectName, projectPath, fileList):
        self.obj_appconfig.print_info(f"Opening project '{projectName}'. Found {len(fileList)} total files.")
        projectDock = QtWidgets.QDockWidget(projectName, self)
        projectDock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)

        tabWidget = QtWidgets.QTabWidget()
        tabWidget.setTabsClosable(True)
        tabWidget.tabCloseRequested.connect(lambda index: tabWidget.removeTab(index))

        # Make tab file names more visible and readable
        tabWidget.setStyleSheet("""
        QTabBar::tab {
            font-size: 8pt;
        }
        QTabBar::tab:selected {
            font-weight: bold;
        }
        """)
        tabWidget.setElideMode(QtCore.Qt.ElideMiddle)

        files_added = 0
        for f_name in fileList:
            filePath = os.path.join(projectPath, f_name)
            # Filter out kicad cache/rescue files
            if f_name.endswith(('.lib', '.sch-bak', '.kicad_pcb-bak', '.net', '.xml', '.cir', '.log')):
                self.obj_appconfig.print_info(f"Skipping file: {f_name}")
                continue

            try:
                with open(filePath, 'r', errors='ignore') as f:
                    content = f.read()

                editor = QtWidgets.QTextEdit()
                editor.setText(content)
                # Set a monospace font
                font = QtGui.QFont()
                font.setFamily("monospace")
                font.setStyleHint(QtGui.QFont.Monospace)
                editor.setFont(font)

                tabWidget.addTab(editor, f_name)
                tabWidget.setTabToolTip(tabWidget.count() - 1, f_name)
                files_added += 1
            except Exception as e:
                self.obj_appconfig.print_info(f"Error reading file {filePath}: {e}")

        self.obj_appconfig.print_info(f"Added {files_added} files to the new tab.")

        if tabWidget.count() > 0:
            projectDock.setWidget(tabWidget)
            self.obj_dockarea.addDockWidget(QtCore.Qt.TopDockWidgetArea, projectDock)
            self.obj_appconfig.print_info("Project dock added to dock area.")

            # Tabify with the welcome widget if it exists
            self.obj_appconfig.print_info("Attempting to tabify with 'Welcome' dock...")
            welcome_dock = None
            for d in self.obj_dockarea.findChildren(QtWidgets.QDockWidget):
                if d.windowTitle() == 'Welcome':
                    welcome_dock = d
                    break

            if welcome_dock:
                self.obj_appconfig.print_info("'Welcome' dock found. Tabifying...")
                self.obj_dockarea.tabifyDockWidget(welcome_dock, projectDock)
                self.obj_appconfig.print_info("Tabify complete.")
            else:
                self.obj_appconfig.print_info("'Welcome' dock NOT found. New dock will appear as a separate window.")

            projectDock.raise_()
            self.obj_appconfig.print_info("Called raise_() on the new project dock.")
        else:
            self.obj_appconfig.print_info(f"No viewable files found in project '{projectName}'. Nothing to display.")

def ensure_config_directory():
    
    if os.name == 'nt':
        user_home = os.path.join('library', 'config')
    else:
        user_home = os.path.expanduser('~')
    
    esim_config_dir = os.path.join(user_home, '.esim')
    
    # Create directory if it doesn't exist
    if not os.path.exists(esim_config_dir):
        os.makedirs(esim_config_dir, exist_ok=True)
    
    return user_home
    
# It is main function of the module and starts the application
def main(args):
    """
    The splash screen opened at the starting of screen is performed
    by this function.
    """
    print("Starting eSim......")
    app = QtWidgets.QApplication(args)
    app.setApplicationName("eSim")

    appView = Application()
    appView.hide()

    splash_pix = QtGui.QPixmap(init_path + 'images/splash_screen_esim.png')
    splash = QtWidgets.QSplashScreen(
        appView, splash_pix, QtCore.Qt.WindowStaysOnTopHint
    )
    splash.setMask(splash_pix.mask())
    splash.setDisabled(True)
    splash.show()

    appView.splash = splash
    appView.obj_workspace.returnWhetherClickedOrNot(appView)

    try:
        if os.name == 'nt':
            user_home = os.path.join('library', 'config')
        else:
            user_home = os.path.expanduser('~')

        user_home = ensure_config_directory()  # Add this line
        file = open(os.path.join(user_home, ".esim/workspace.txt"), 'w')
        work = int(file.read(1))
        file.close()
    except IOError:
        work = 0

    if work != 0:
        appView.obj_workspace.defaultWorkspace()
    else:
        appView.obj_workspace.show()

    sys.exit(app.exec_())


# Call main function
if __name__ == '__main__':
    # Create and display the splash screen
    try:
        main(sys.argv)
    except Exception as err:
        import traceback
        traceback.print_exc()
        print("Error: ", err)
