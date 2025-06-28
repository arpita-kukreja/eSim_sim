from PyQt5 import QtCore, QtGui, QtWidgets, uic
import os


class TerminalUi(QtWidgets.QMainWindow):
    """This is a class that represents the GUI required to provide
    details regarding the ngspice simulation. This GUI consists of
    a progress bar, a console window which displays the log of the
    simulation and button required for re-simulation and cancellation
    of the simulation"""
    def __init__(self, qProcess, args):
        """The constructor of the TerminalUi class
        param: qProcess: a PyQt QProcess that runs ngspice
        type: qProcess: :class:`QtCore.QProcess`
        param: args: arguments to be passed on to the ngspice call
        type: args: list
        """
        super(TerminalUi, self).__init__()

        # Other variables
        self.darkColor = True
        self.qProcess = qProcess
        self.args = args
        self.iconDir = "../../images"

        # Load the ui file
        uic.loadUi("TerminalUi.ui", self)

        # Define Our Widgets
        self.progressBar = self.findChild(
            QtWidgets.QProgressBar,
            "progressBar"
        )
        self.simulationConsole = self.findChild(
            QtWidgets.QTextEdit,
            "simulationConsole"
        )

        self.lightDarkModeButton = self.findChild(
            QtWidgets.QPushButton,
            "lightDarkModeButton"
        )
        self.cancelSimulationButton = self.findChild(
            QtWidgets.QPushButton,
            "cancelSimulationButton"
        )
        self.cancelSimulationButton.setEnabled(True)

        self.redoSimulationButton = self.findChild(
            QtWidgets.QPushButton,
            "redoSimulationButton"
        )
        self.redoSimulationButton.setEnabled(False)

        # Add functionalities to Widgets
        self.lightDarkModeButton.setIcon(
            QtGui.QIcon(
                os.path.join(
                    self.iconDir,
                    'light_mode.png'
                )
            )
        )
        self.lightDarkModeButton.clicked.connect(self.changeColor)
        self.cancelSimulationButton.clicked.connect(self.cancelSimulation)
        self.redoSimulationButton.clicked.connect(self.redoSimulation)

        self.simulationCancelled = False

        # --- Force correct theme and size immediately ---
        # Try to get the current theme from parent if possible
        is_dark_theme = True
        app_parent = self.parent()
        while app_parent is not None:
            if hasattr(app_parent, 'is_dark_theme'):
                is_dark_theme = app_parent.is_dark_theme
                break
            app_parent = app_parent.parent() if hasattr(app_parent, 'parent') else None
        self.set_theme(is_dark_theme)

        self.show()

    def cancelSimulation(self):
        """This function cancels the ongoing ngspice simulation.
        """
        self.cancelSimulationButton.setEnabled(False)
        self.redoSimulationButton.setEnabled(True)

        if (self.qProcess.state() == QtCore.QProcess.NotRunning):
            return

        self.simulationCancelled = True
        self.qProcess.kill()

        # To show progressBar completed
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 100)

        cancelFormat = '<span style="color:#FF8624; font-size:26px;">{}</span>'
        self.simulationConsole.append(
            cancelFormat.format("Simulation Cancelled!"))
        self.simulationConsole.verticalScrollBar().setValue(
            self.simulationConsole.verticalScrollBar().maximum()
        )

    def redoSimulation(self):
        """This function reruns the ngspice simulation
        """
        self.Flag = "Flase"
        self.cancelSimulationButton.setEnabled(True)
        self.redoSimulationButton.setEnabled(False)

        if (self.qProcess.state() != QtCore.QProcess.NotRunning):
            return

        # To make the progressbar running
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", -1)

        self.simulationConsole.setText("")
        self.simulationCancelled = False

        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Ngspice Plots")
        msg_box.setText("Do you want Ngspice plots?")
        
        yes_button = msg_box.addButton("Yes", QtWidgets.QMessageBox.YesRole)
        no_button = msg_box.addButton("No", QtWidgets.QMessageBox.NoRole)

        msg_box.exec_()

        if msg_box.clickedButton() == yes_button:
            self.Flag = True 
        else:
            self.Flag = False  

        # Emit a custom signal with name plotFlag2 depending upon the Flag
        self.qProcess.setProperty("plotFlag2", self.Flag)

        self.qProcess.start('ngspice', self.args)

    def changeColor(self):
        """Toggles the :class:`Ui_Form` console between dark mode
                        and light mode
        """
        if self.darkColor is True:
            self.simulationConsole.setStyleSheet("QTextEdit {\n \
                background-color: white;\n \
                color: black;\n \
            }")
            self.lightDarkModeButton.setIcon(
                QtGui.QIcon(
                    os.path.join(
                        self.iconDir,
                        "dark_mode.png"
                        )
                    )
                )
            self.darkColor = False
        else:
            self.simulationConsole.setStyleSheet("QTextEdit {\n \
                background-color: rgb(36, 31, 49);\n \
                color: white;\n \
            }")
            self.lightDarkModeButton.setIcon(
                QtGui.QIcon(
                    os.path.join(
                        self.iconDir,
                        "light_mode.png"
                        )
                    )
                )
            self.darkColor = True

    def set_theme(self, is_dark_theme):
        """Update the theme and re-apply styling to all widgets."""
        self.darkColor = is_dark_theme
        if is_dark_theme:
            # Dark theme styles
            self.setStyleSheet("""
                QWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0e1a, stop:0.3 #1a1d29, stop:0.7 #1e2124, stop:1 #0f1419); color: #e8eaed; font-family: 'Fira Sans', 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif; font-size: 17px; font-weight: 500; }
                QTextEdit, QLineEdit, QPlainTextEdit { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #23273a, stop:1 #181b24); color: #e8eaed; border: 2px solid #2d3142; border-radius: 12px; padding: 20px 24px; font-weight: 500; font-size: 18px; selection-background-color: #40c4ff; selection-color: #181b24; background-clip: padding-box; }
                QTextEdit:focus, QLineEdit:focus, QPlainTextEdit:focus { border: 2px solid #40c4ff; background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2a2e41, stop:1 #1f222b); }
                QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #40c4ff, stop:1 #1976d2); color: #181b24; border: 2px solid #40c4ff; padding: 16px 32px; border-radius: 12px; font-weight: 700; font-size: 18px; letter-spacing: 0.5px; min-width: 120px; }
                QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1976d2, stop:1 #0d47a1); color: #fff; border: 2px solid #1976d2; transform: translateY(-2px); }
                QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #23273a, stop:1 #1a1e27); color: #40c4ff; border: 2px solid #40c4ff; transform: translateY(0px); }
                QPushButton#lightDarkModeButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d3142, stop:1 #23273a); border: 2px solid #40c4ff; border-radius: 18px; padding: 8px; min-width: 35px; max-width: 35px; font-size: 16px; }
                QPushButton#lightDarkModeButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #40c4ff, stop:1 #1976d2); color: #181b24; }
                QLabel { color: #e8eaed; font-weight: 600; font-size: 18px; letter-spacing: 0.2px; padding: 4px 0px; }
                QProgressBar { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #23273a, stop:1 #1a1e27); border: 2px solid #2d3142; border-radius: 12px; text-align: center; color: #e8eaed; font-weight: 600; font-size: 18px; padding: 2px; }
                QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #40c4ff, stop:0.5 #1976d2, stop:1 #40c4ff); border-radius: 10px; margin: 1px; }
                QWidget#verticalLayoutWidget { background: rgba(45, 49, 66, 0.3); border-radius: 16px; border: 1px solid rgba(64, 196, 255, 0.1); }
            """)
            self.lightDarkModeButton.setIcon(QtGui.QIcon(os.path.join(self.iconDir, 'light_mode.png')))
        else:
            # Light theme styles
            self.setStyleSheet("""
                QWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f8f9fa); color: #2c3e50; font-family: 'Fira Sans', 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif; font-size: 17px; font-weight: 500; }
                QTextEdit, QLineEdit, QPlainTextEdit { background: #ffffff; color: #2c3e50; border: 2px solid #b0bec5; border-radius: 12px; padding: 20px 24px; font-weight: 500; font-size: 18px; selection-background-color: #1976d2; selection-color: #ffffff; background-clip: padding-box; }
                QTextEdit:focus, QLineEdit:focus, QPlainTextEdit:focus { border: 2px solid #1976d2; background: #f8f9fa; }
                QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1976d2, stop:1 #1565c0); color: #ffffff; border: 2px solid #1976d2; padding: 16px 32px; border-radius: 12px; font-weight: 700; font-size: 18px; letter-spacing: 0.5px; min-width: 120px; }
                QPushButton:hover { background: #1565c0; color: #fff; border: 2px solid #1565c0; transform: translateY(-2px); }
                QPushButton:pressed { background: #0d47a1; color: #ffffff; border: 2px solid #0d47a1; transform: translateY(0px); }
                QPushButton#lightDarkModeButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e3e8ee, stop:1 #f5f7fa); border: 2px solid #1976d2; border-radius: 18px; padding: 8px; min-width: 35px; max-width: 35px; font-size: 16px; }
                QPushButton#lightDarkModeButton:hover { background: #1976d2; color: #fff; }
                QLabel { color: #2c3e50; font-weight: 600; font-size: 18px; letter-spacing: 0.2px; padding: 4px 0px; }
                QProgressBar { background: #f8f9fa; border: 2px solid #b0bec5; border-radius: 12px; text-align: center; color: #2c3e50; font-weight: 600; font-size: 18px; padding: 2px; }
                QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976d2, stop:0.5 #1565c0, stop:1 #1976d2); border-radius: 10px; margin: 1px; }
                QWidget#verticalLayoutWidget { background: rgba(25, 118, 210, 0.05); border-radius: 16px; border: 1px solid rgba(25, 118, 210, 0.1); }
            """)
            self.lightDarkModeButton.setIcon(QtGui.QIcon(os.path.join(self.iconDir, 'light_mode.png')))

        # --- Enforce button sizes and fonts to match CSS ---
        btn_font = QtGui.QFont("Fira Sans", 18, QtGui.QFont.Bold)
        for btn in [self.redoSimulationButton, self.cancelSimulationButton]:
            btn.setMinimumHeight(56)
            btn.setMinimumWidth(140)
            btn.setFont(btn_font)
        self.lightDarkModeButton.setMinimumSize(35, 35)
        self.lightDarkModeButton.setMaximumSize(35, 35)
        self.lightDarkModeButton.setFont(QtGui.QFont("Fira Sans", 16, QtGui.QFont.Bold))
