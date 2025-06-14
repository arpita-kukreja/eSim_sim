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

        # Set slot for simulation end signal to plot simulation data
        self.simulationEndSignal.connect(self.plotSimulationData)

        #the plotFlag
        self.plotFlag = False

        # Creating require Object
        self.obj_workspace = Workspace.Workspace()
        self.obj_Mainview = MainView()
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

        font = QtGui.QFont("Fira Sans", 11)
        self.setFont(font)

        self.statusBar = self.statusBar()
        self.statusBar.showMessage('Welcome to eSim!')

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
        self.newproj.triggered.connect(self.new_project)

        self.openproj = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/openProject.png'),
            'Open Project', self
        )
        self.openproj.setShortcut('Ctrl+O')
        self.openproj.triggered.connect(self.open_project)

        self.closeproj = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/closeProject.png'),
            'Close Project', self
        )
        self.closeproj.setShortcut('Ctrl+X')
        self.closeproj.triggered.connect(self.close_project)

        self.wrkspce = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/workspace.ico'),
            'Change Workspace', self
        )
        self.wrkspce.setShortcut('Ctrl+W')
        self.wrkspce.triggered.connect(self.change_workspace)

        self.helpfile = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/helpProject.png'),
            'Help', self
        )
        self.helpfile.setShortcut('Ctrl+H')
        self.helpfile.triggered.connect(self.help_project)

        # Theme toggle button - set initial icon for dark mode since we're in light mode
        self.theme_toggle = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/dark_mode.png'),
            'Switch Theme', self
        )
        self.theme_toggle.setShortcut('Ctrl+T')
        self.theme_toggle.triggered.connect(self.toggle_theme)
        self.theme_toggle.setToolTip('Switch to Dark Mode')

        # added devDocs logo and called functions
        self.devdocs = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/dev_docs.png'),
            'Dev Docs', self
        )
        self.devdocs.setShortcut('Ctrl+D')
        self.devdocs.triggered.connect(self.dev_docs)

        self.topToolbar = self.addToolBar('Top Tool Bar')
        self.topToolbar.addAction(self.newproj)
        self.topToolbar.addAction(self.openproj)
        self.topToolbar.addAction(self.closeproj)
        self.topToolbar.addAction(self.wrkspce)
        self.topToolbar.addAction(self.helpfile)
        self.topToolbar.addAction(self.devdocs)
        self.topToolbar.addAction(self.theme_toggle)
        self.topToolbar.setIconSize(QSize(24, 24))
        self.topToolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        
        # Add specific styling for top toolbar
        # self.topToolbar.setStyleSheet("""
        #     QToolBar {
        #         spacing: 10px;
        #         padding: 4px;
        #     }
        #     QToolButton {
        #         min-width: 100px;
        #         max-width: 140px;
        #         min-height: 54px;
        #         padding: 4px 2px;
        #         margin: 1px;
        #         font-size: 10.5px;
        #         color: #000000;
        #         background: transparent;
        #         border: none;
        #         text-align: center;
        #         white-space: nowrap;
        #     }
        #     QToolButton:hover {
        #         color: #40c4ff;
        #     }
        # """)

        # This part is setting fossee logo to the right
        # corner in the application window.
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
        self.kicad.triggered.connect(self.obj_kicad.openSchematic)

        self.conversion = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/ki-ng.png'),
            'Convert KiCad to Ngspice', self
        )
        self.conversion.triggered.connect(self.obj_kicad.openKicadToNgspice)

        self.ngspice = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/ngspice.png'),
            'Simulate', self
        )
        self.ngspice.triggered.connect(self.plotFlagPopBox)

        self.model = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/model.png'),
            'Model Editor', self
        )
        self.model.triggered.connect(self.open_modelEditor)

        self.subcircuit = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/subckt.png'),
            'Subcircuit', self
        )
        self.subcircuit.triggered.connect(self.open_subcircuit)

        self.nghdl = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/nghdl.png'), 'NGHDL', self
        )
        self.nghdl.triggered.connect(self.open_nghdl)

        self.makerchip = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/makerchip.png'),
            'Makerchip-NgVeri', self
        )
        self.makerchip.triggered.connect(self.open_makerchip)

        self.omedit = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/omedit.png'),
            'Modelica Converter', self
        )
        self.omedit.triggered.connect(self.open_OMedit)

        self.omoptim = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/omoptim.png'),
            'OM Optimisation', self
        )
        self.omoptim.triggered.connect(self.open_OMoptim)

        self.conToeSim = QtWidgets.QAction(
            QtGui.QIcon(init_path + 'images/icon.png'),
            'Schematics converter', self
        )
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
                font-size: 9px;
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
            QDockWidget[orientation="horizontal"] QWidget {
                background: transparent;
            }
            QDockWidget[orientation="horizontal"] QVBoxLayout {
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: flex-start;
                align-items: center;
            }
            QDockWidget[orientation="horizontal"] QToolButton {
                min-width: 120px;
                min-height: 40px;
                margin: 1px;
                padding: 2px;
            }
        """)

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
            self.theme_toggle.setIcon(QtGui.QIcon(init_path + 'images/light_mode.png'))
            self.theme_toggle.setToolTip('Switch to Light Mode')
            # Update simulation tab and graph colors for dark theme
            self.update_simulation_theme(is_dark=True)
        else:
            self.apply_light_theme()
            self.theme_toggle.setIcon(QtGui.QIcon(init_path + 'images/dark_mode.png'))
            self.theme_toggle.setToolTip('Switch to Dark Mode')
            # Update simulation tab and graph colors for light theme
            self.update_simulation_theme(is_dark=False)

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

        # Force update of the UI
        self.repaint()

    def update_simulation_theme(self, is_dark):
        """Update simulation tab and graph colors based on theme."""
        if is_dark:
            # Dark theme colors for simulation
            simulation_style = """
                QTextEdit, QPlainTextEdit {
                    background: #23273a;
                    color: #e8eaed;
                    border: 1px solid #181b24;
                    border-radius: 8px;
                    selection-background-color: #40c4ff;
                    selection-color: #181b24;
                }
                QLineEdit {
                    background: #23273a;
                    color: #e8eaed;
                    border: 1px solid #181b24;
                    border-radius: 8px;
                    selection-background-color: #40c4ff;
                    selection-color: #181b24;
                }
                QLabel {
                    color: #e8eaed;
                }
                QProgressBar {
                    background: #181b24;
                    border: 1px solid #23273a;
                    border-radius: 8px;
                    text-align: center;
                    color: #e8eaed;
                }
                QProgressBar::chunk {
                    background: #40c4ff;
                    border-radius: 8px;
                }
            """
            # Dark theme colors for graphs
            graph_style = {
                'background': '#23273a',
                'text_color': '#e8eaed',
                'grid_color': '#181b24',
                'line_colors': ['#40c4ff', '#ff4081', '#00e676', '#ffd600', '#ff6d00']
            }
        else:
            # Light theme colors for simulation
            simulation_style = """
                QTextEdit, QPlainTextEdit {
                    background: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #e1e4e8;
                    border-radius: 8px;
                    selection-background-color: #1976d2;
                    selection-color: #ffffff;
                }
                QLineEdit {
                    background: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #e1e4e8;
                    border-radius: 8px;
                    selection-background-color: #1976d2;
                    selection-color: #ffffff;
                }
                QLabel {
                    color: #2c3e50;
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
            """
            # Light theme colors for graphs
            graph_style = {
                'background': '#ffffff',
                'text_color': '#2c3e50',
                'grid_color': '#e1e4e8',
                'line_colors': ['#1976d2', '#d81b60', '#00897b', '#fbc02d', '#e64a19']
            }

        # Apply simulation styles
        for widget in self.findChildren((QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit, QtWidgets.QLineEdit, QtWidgets.QLabel, QtWidgets.QProgressBar)):
            if widget.parent() and isinstance(widget.parent(), QtWidgets.QDockWidget):
                if "Simulation" in widget.parent().windowTitle():
                    widget.setStyleSheet(simulation_style)

        # Update graph colors if matplotlib is being used
        try:
            import matplotlib.pyplot as plt
            plt.style.use('dark_background' if is_dark else 'default')
            # Update any existing plots
            for figure in plt.get_fignums():
                fig = plt.figure(figure)
                ax = fig.gca()
                ax.set_facecolor(graph_style['background'])
                ax.tick_params(colors=graph_style['text_color'])
                ax.xaxis.label.set_color(graph_style['text_color'])
                ax.yaxis.label.set_color(graph_style['text_color'])
                ax.title.set_color(graph_style['text_color'])
                ax.grid(True, color=graph_style['grid_color'])
                fig.set_facecolor(graph_style['background'])
                plt.draw()
        except ImportError:
            pass  # matplotlib not available

        # Update plot window theme if it exists
        try:
            from ngspiceSimulation.pythonPlotting import plotWindow
            if plotWindow.instance is not None:
                if plotWindow.instance.is_dark_theme != is_dark:
                    plotWindow.instance.toggle_theme()
        except ImportError:
            pass  # plotWindow not available

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
        """
        This function call changes Workspace
        """
        print("Function : Change Workspace")
        self.obj_workspace.returnWhetherClickedOrNot(self)
        self.hide()
        self.obj_workspace.show()

    def help_project(self):
        """
        This function opens usermanual in dockarea.
            - It prints the message ""Function : Help""
            - Uses print_info() method of class Appconfig
              from Configuration/Appconfig.py file.
            - Call method usermanual() from ./DockArea.py.
        """
        print("Function : Help")
        self.obj_appconfig.print_info('Help is called')
        print("Current Project is : ", self.obj_appconfig.current_project)
        self.obj_Mainview.obj_dockarea.usermanual()

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

            self.obj_Mainview.obj_dockarea.ngspiceEditor(
                projName, ngspiceNetlist, self.simulationEndSignal, self.plotFlag)

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

    def __init__(self, *args):
        # call init method of superclass
        QtWidgets.QWidget.__init__(self, *args)

        self.obj_appconfig = Appconfig()

        self.leftSplit = QtWidgets.QSplitter()
        self.middleSplit = QtWidgets.QSplitter()

        self.mainLayout = QtWidgets.QVBoxLayout()
        # Intermediate Widget
        self.middleContainer = QtWidgets.QWidget()
        self.middleContainerLayout = QtWidgets.QVBoxLayout()

        # Area to be included in MainView
        self.noteArea = QtWidgets.QTextEdit()
        self.noteArea.setReadOnly(True)
        self.noteArea.setAcceptRichText(True)
        self.noteArea.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1.5px solid #23273a;
                border-radius: 14px;
                padding: 18px 24px;
                font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
                font-size: 15px;
                font-weight: 500;
                letter-spacing: 0.1px;
            }
            QTextEdit QScrollBar:vertical, QTextEdit QScrollBar:horizontal {
                background: #23273a;
                border-radius: 6px;
            }
            QTextEdit a {
                color: #40c4ff;
                text-decoration: none;
                font-weight: 600;
            }
        """)
        welcome_html = '''
<div style="color: #e8eaed; background-color: transparent; font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;">
    <h2 style="color: #e8eaed; margin-bottom: 16px; font-weight: 700; letter-spacing: 0.5px;">
        Welcome to <span style='color: #40c4ff; font-weight: 700;'>eSim</span>
    </h2>
    <p style="color: #e8eaed; margin-bottom: 14px; line-height: 1.6; font-weight: 500;">
        <b style="color: #40c4ff; font-weight: 700;">eSim</b> is an open source EDA tool for circuit design, simulation, analysis and PCB design.<br>
        It is an integrated tool built using open source software such as
        <a href="https://www.kicad.org/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">KiCad</a>,
        <a href="https://ngspice.sourceforge.io/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">Ngspice</a>,
        <a href="http://ghdl.free.fr" style="color: #40c4ff; text-decoration: none; font-weight: 600;">GHDL</a>,
        <a href="https://www.veripool.org/verilator/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">Verilator</a>,
        <a href="https://www.makerchip.com/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">Makerchip IDE</a>, and
        <a href="https://skywater-pdk.rtfd.io/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">SkyWater SKY130 PDK</a>.<br>
        eSim source is released under <b style="color: #40c4ff; font-weight: 700;">GNU General Public License</b>.
    </p>
    <p style="color: #e8eaed; margin-bottom: 14px; line-height: 1.6; font-weight: 500;">
        This tool is developed by the <b style="color: #40c4ff; font-weight: 700;">eSim Team at FOSSEE, IIT Bombay</b>.<br>
        To know more about eSim, please visit:
        <a href="https://esim.fossee.in/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">https://esim.fossee.in/</a>.
    </p>
    <p style="color: #e8eaed; margin-bottom: 14px; line-height: 1.6; font-weight: 500;">
        To discuss more about eSim, please visit:
        <a href="https://forums.fossee.in/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">https://forums.fossee.in/</a>
    </p>
</div>
'''
        self.noteArea.setHtml(welcome_html)

        self.obj_dockarea = DockArea.DockArea()
        self.obj_projectExplorer = ProjectExplorer.ProjectExplorer()

        # Adding content to vertical middle Split.
        self.middleSplit.setOrientation(QtCore.Qt.Vertical)
        self.middleSplit.addWidget(self.obj_dockarea)
        self.middleSplit.addWidget(self.noteArea)

        # Adding middle split to Middle Container Widget
        self.middleContainerLayout.addWidget(self.middleSplit)
        self.middleContainer.setLayout(self.middleContainerLayout)

        # Adding content of left split
        self.leftSplit.addWidget(self.obj_projectExplorer)
        self.leftSplit.addWidget(self.middleContainer)

        # Adding to main Layout
        self.mainLayout.addWidget(self.leftSplit)
        self.leftSplit.setSizes([int(self.width() / 4.5), self.height()])
        self.middleSplit.setSizes([self.width(), int(self.height() / 2)])
        self.setLayout(self.mainLayout)

        # Initialize welcome message with light theme by default
        self.welcome_browser = QtWidgets.QTextBrowser()
        self.apply_light_theme_welcome()

    def apply_dark_theme_welcome(self):
        """Apply dark theme to welcome message"""
        welcome_html = '''
        <div style="color: #e8eaed; background-color: transparent; font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;">
            <h2 style="color: #e8eaed; margin-bottom: 16px; font-weight: 700; letter-spacing: 0.5px;">
                Welcome to <span style='color: #40c4ff; font-weight: 700;'>eSim</span>
            </h2>
            <p style="color: #e8eaed; margin-bottom: 14px; line-height: 1.6; font-weight: 500;">
                <b style="color: #40c4ff; font-weight: 700;">eSim</b> is an open source EDA tool for circuit design, simulation, analysis and PCB design.<br>
                It is an integrated tool built using open source software such as
                <a href="https://www.kicad.org/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">KiCad</a>,
                <a href="https://ngspice.sourceforge.io/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">Ngspice</a>,
                <a href="http://ghdl.free.fr" style="color: #40c4ff; text-decoration: none; font-weight: 600;">GHDL</a>,
                <a href="https://www.veripool.org/verilator/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">Verilator</a>,
                <a href="https://www.makerchip.com/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">Makerchip IDE</a>, and
                <a href="https://skywater-pdk.rtfd.io/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">SkyWater SKY130 PDK</a>.<br>
                eSim source is released under <b style="color: #40c4ff; font-weight: 700;">GNU General Public License</b>.
            </p>
            <p style="color: #e8eaed; margin-bottom: 14px; line-height: 1.6; font-weight: 500;">
                This tool is developed by the <b style="color: #40c4ff; font-weight: 700;">eSim Team at FOSSEE, IIT Bombay</b>.<br>
                To know more about eSim, please visit:
                <a href="https://esim.fossee.in/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">https://esim.fossee.in/</a>.
            </p>
            <p style="color: #e8eaed; margin-bottom: 14px; line-height: 1.6; font-weight: 500;">
                To discuss more about eSim, please visit:
                <a href="https://forums.fossee.in/" style="color: #40c4ff; text-decoration: none; font-weight: 600;">https://forums.fossee.in/</a>
            </p>
        </div>
        '''
        self.welcome_browser.setHtml(welcome_html)
        self.welcome_browser.setStyleSheet('''
            QTextBrowser {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #23273a;
                border-radius: 12px;
                padding: 16px;
                selection-background-color: #40c4ff;
                selection-color: #181b24;
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
        ''')

    def apply_light_theme_welcome(self):
        """Apply light theme to welcome message"""
        welcome_html = '''
        <div style="color: #2c3e50; background-color: transparent; font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;">
            <h2 style="color: #2c3e50; margin-bottom: 16px; font-weight: 700; letter-spacing: 0.5px;">
                Welcome to <span style='color: #1976d2; font-weight: 700;'>eSim</span>
            </h2>
            <p style="color: #2c3e50; margin-bottom: 14px; line-height: 1.6; font-weight: 500;">
                <b style="color: #1976d2; font-weight: 700;">eSim</b> is an open source EDA tool for circuit design, simulation, analysis and PCB design.<br>
                It is an integrated tool built using open source software such as
                <a href="https://www.kicad.org/" style="color: #1976d2; text-decoration: none; font-weight: 600;">KiCad</a>,
                <a href="https://ngspice.sourceforge.io/" style="color: #1976d2; text-decoration: none; font-weight: 600;">Ngspice</a>,
                <a href="http://ghdl.free.fr" style="color: #1976d2; text-decoration: none; font-weight: 600;">GHDL</a>,
                <a href="https://www.veripool.org/verilator/" style="color: #1976d2; text-decoration: none; font-weight: 600;">Verilator</a>,
                <a href="https://www.makerchip.com/" style="color: #1976d2; text-decoration: none; font-weight: 600;">Makerchip IDE</a>, and
                <a href="https://skywater-pdk.rtfd.io/" style="color: #1976d2; text-decoration: none; font-weight: 600;">SkyWater SKY130 PDK</a>.<br>
                eSim source is released under <b style="color: #1976d2; font-weight: 700;">GNU General Public License</b>.
            </p>
            <p style="color: #2c3e50; margin-bottom: 14px; line-height: 1.6; font-weight: 500;">
                This tool is developed by the <b style="color: #1976d2; font-weight: 700;">eSim Team at FOSSEE, IIT Bombay</b>.<br>
                To know more about eSim, please visit:
                <a href="https://esim.fossee.in/" style="color: #1976d2; text-decoration: none; font-weight: 600;">https://esim.fossee.in/</a>.
            </p>
            <p style="color: #2c3e50; margin-bottom: 14px; line-height: 1.6; font-weight: 500;">
                To discuss more about eSim, please visit:
                <a href="https://forums.fossee.in/" style="color: #1976d2; text-decoration: none; font-weight: 600;">https://forums.fossee.in/</a>
            </p>
        </div>
        '''
        self.welcome_browser.setHtml(welcome_html)
        self.welcome_browser.setStyleSheet('''
            QTextBrowser {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                color: #2c3e50;
                border: 1px solid #e1e4e8;
                border-radius: 12px;
                padding: 16px;
                selection-background-color: #1976d2;
                selection-color: #ffffff;
            }
            QScrollBar:vertical {
                background: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #e1e4e8;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #1976d2;
            }
        ''')

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
        print("Error: ", err)
