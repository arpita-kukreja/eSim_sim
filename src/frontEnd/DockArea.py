from PyQt5 import QtCore, QtWidgets
from ngspiceSimulation.pythonPlotting import plotWindow
from ngspiceSimulation.NgspiceWidget import NgspiceWidget
from configuration.Appconfig import Appconfig
from modelEditor.ModelEditor import ModelEditorclass
from subcircuit.Subcircuit import Subcircuit
from maker.makerchip import makerchip
from kicadtoNgspice.KicadtoNgspice import MainWindow
from browser.Welcome import Welcome
from browser.UserManual import UserManual
from ngspicetoModelica.ModelicaUI import OpenModelicaEditor
from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
import os
from converter.pspiceToKicad import PspiceConverter
from converter.ltspiceToKicad import LTspiceConverter
from converter.LtspiceLibConverter import LTspiceLibConverter
from converter.libConverter import PspiceLibConverter
from converter.browseSchematics import browse_path
dockList = ['Welcome']
count = 1
dock = {}


class DockArea(QtWidgets.QMainWindow):
    """
    This class contains function for designing UI of all the editors
    in dock area part:

        - Test Editor.
        - Model Editor.
        - Python Plotting.
        - Ngspice Editor.
        - Kicad to Ngspice Editor.
        - Subcircuit Editor.
        - Modelica editor.
    """

    def __init__(self):
        """This act as constructor for class DockArea."""
        QtWidgets.QMainWindow.__init__(self)
        self.obj_appconfig = Appconfig()

        # Set the dock options for better tab appearance
        self.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks | 
                          QtWidgets.QMainWindow.AnimatedDocks)
        
        # Set tab position to top
        self.setTabPosition(QtCore.Qt.AllDockWidgetAreas, QtWidgets.QTabWidget.North)
        
        # Set document mode for modern look
        self.setDocumentMode(True)

        # Set custom style for dock widgets and tabs
        self.setStyleSheet("""
            QDockWidget {
                border: 1px solid #23273a;
                border-radius: 4px;
                margin-top: 4px;
            }
            
            QDockWidget::title {
                text-align: center;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                padding: 6px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                padding: 6px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
                max-width: 180px;
                font-weight: 500;
                font-size: 9pt;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #40c4ff, stop:1 #2d8cff);
                color: #181b24;
                border-bottom: 2px solid #40c4ff;
            }
            
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d3a4b, stop:1 #1e2530);
            }
            
            QTabWidget::pane {
                border: 1px solid #23273a;
                border-radius: 4px;
                background: #181b24;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
            }

            QTabBar::close-button {
                image: url(close.png);
                subcontrol-position: right;
            }
            
            QTabBar::close-button:hover {
                background: #ff4444;
                border-radius: 2px;
            }
        """)

        for dockName in dockList:
            dock[dockName] = QtWidgets.QDockWidget(dockName)
            dock[dockName].setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | 
                                     QtWidgets.QDockWidget.DockWidgetFloatable)
            self.welcomeWidget = QtWidgets.QWidget()
            self.welcomeLayout = QtWidgets.QVBoxLayout()
            # Set smaller margins for the layout
            self.welcomeLayout.setContentsMargins(4, 4, 4, 4)
            self.welcomeLayout.setSpacing(4)
            self.welcomeLayout.addWidget(Welcome())  # Call browser

            # Adding to main Layout
            self.welcomeWidget.setLayout(self.welcomeLayout)
            dock[dockName].setWidget(self.welcomeWidget)
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock[dockName])

        self.show()

    def createTestEditor(self):
        """This function create widget for Library Editor"""
        global count

        self.testWidget = QtWidgets.QWidget()
        self.testArea = QtWidgets.QTextEdit()
        self.testLayout = QtWidgets.QVBoxLayout()
        # Set smaller margins for the layout
        self.testLayout.setContentsMargins(4, 4, 4, 4)
        self.testLayout.setSpacing(4)
        self.testLayout.addWidget(self.testArea)

        # Adding to main Layout
        self.testWidget.setLayout(self.testLayout)
        dock['Tips-' + str(count)] = QtWidgets.QDockWidget('Tips-' + str(count))
        dock['Tips-' + str(count)].setWidget(self.testWidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock['Tips-' + str(count)])
        self.tabifyDockWidget(dock['Welcome'], dock['Tips-' + str(count)])

        dock['Tips-' + str(count)].setVisible(True)
        dock['Tips-' + str(count)].setFocus()
        dock['Tips-' + str(count)].raise_()

        temp = self.obj_appconfig.current_project['ProjectName']
        if temp:
            self.obj_appconfig.dock_dict[temp].append(dock['Tips-' + str(count)])
        count = count + 1

    def plottingEditor(self):
        """This function creates or updates the widget for interactive PythonPlotting, now as a single instance with navigation."""
        self.projDir = self.obj_appconfig.current_project["ProjectName"]
        self.projName = os.path.basename(self.projDir)
        # Use the static add_output method to manage outputs and window
        from ngspiceSimulation.pythonPlotting import plotWindow
        plotWindow.add_output(self.projDir, self.projName)
        # Bring the window to focus if it exists
        if plotWindow.instance:
            plotWindow.instance.show()
            plotWindow.instance.raise_()

    def ngspiceEditor(self, projName, netlist, simEndSignal, plotFlag):
        """ This function creates widget for Ngspice window."""
        global count
        self.ngspiceWidget = QtWidgets.QWidget()

        self.ngspiceLayout = QtWidgets.QVBoxLayout()
        # Set smaller margins for the layout
        self.ngspiceLayout.setContentsMargins(4, 4, 4, 4)
        self.ngspiceLayout.setSpacing(4)
        self.ngspiceLayout.addWidget(NgspiceWidget(netlist, simEndSignal, plotFlag))

        # Adding to main Layout
        self.ngspiceWidget.setLayout(self.ngspiceLayout)
        dockName = f'Simulation-{projName}-'
        dock[dockName + str(count)] = QtWidgets.QDockWidget(dockName + str(count))
        dock[dockName + str(count)].setWidget(self.ngspiceWidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock[dockName + str(count)])
        self.tabifyDockWidget(dock['Welcome'], dock[dockName + str(count)])

        dock[dockName + str(count)].setVisible(True)
        dock[dockName + str(count)].setFocus()
        dock[dockName + str(count)].raise_()

        temp = self.obj_appconfig.current_project['ProjectName']
        if temp:
            self.obj_appconfig.dock_dict[temp].append(dock[dockName + str(count)])
        count = count + 1

    def eSimConverter(self):
        """This function creates a widget for eSimConverter."""
        global count

        dockName = 'Schematics Converter-'

        self.eConWidget = QtWidgets.QWidget()
        self.eConLayout = QVBoxLayout()  # QVBoxLayout for the main layout

        file_path_layout = QHBoxLayout()  # QHBoxLayout for file path line
        lib_path_layout = QHBoxLayout()

        file_path_text_box = QLineEdit()
        file_path_text_box.setFixedHeight(35)
        file_path_text_box.setFixedWidth(800)
        file_path_text_box.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 2px solid #40c4ff;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: 500;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #40c4ff;
            }
        """)
        file_path_layout.setAlignment(Qt.AlignCenter)
        file_path_layout.addWidget(file_path_text_box)

        browse_button = QPushButton("Browse")
        browse_button.setFixedSize(120, 35)
        browse_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #23273a;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: #40c4ff;
                color: #181b24;
                border: 1px solid #40c4ff;
            }
        """)
        browse_button.clicked.connect(lambda: browse_path(self,file_path_text_box))
        file_path_layout.addWidget(browse_button)

        self.eConLayout.addLayout(file_path_layout)  # Add file path layout to main layout

        button_layout = QHBoxLayout()  # QHBoxLayout for the buttons

        self.pspice_converter = PspiceConverter(self)
        self.ltspice_converter = LTspiceConverter(self)
        self.pspiceLib_converter = PspiceLibConverter(self)
        self.ltspiceLib_converter = LTspiceLibConverter(self)

        upload_button2 = QPushButton("Convert PSpice Library")
        upload_button2.setFixedSize(260, 35)
        upload_button2.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #23273a;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: #40c4ff;
                color: #181b24;
                border: 1px solid #40c4ff;
            }
        """)
        upload_button2.clicked.connect(lambda: self.pspiceLib_converter.upload_file_Pspice(file_path_text_box.text()))
        button_layout.addWidget(upload_button2)

        upload_button1 = QPushButton("Convert PSpice Schematics")
        upload_button1.setFixedSize(260, 35)
        upload_button1.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #23273a;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: #40c4ff;
                color: #181b24;
                border: 1px solid #40c4ff;
            }
        """)
        upload_button1.clicked.connect(lambda: self.pspice_converter.upload_file_Pspice(file_path_text_box.text()))
        button_layout.addWidget(upload_button1)

        upload_button3 = QPushButton("Convert LTspice Library")
        upload_button3.setFixedSize(260, 35)
        upload_button3.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #23273a;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: #40c4ff;
                color: #181b24;
                border: 1px solid #40c4ff;
            }
        """)
        upload_button3.clicked.connect(lambda: self.ltspiceLib_converter.upload_file_LTspice(file_path_text_box.text()))
        button_layout.addWidget(upload_button3)

        upload_button = QPushButton("Convert LTspice Schematics")
        upload_button.setFixedSize(260, 35)
        upload_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #23273a;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: #40c4ff;
                color: #181b24;
                border: 1px solid #40c4ff;
            }
        """)
        upload_button.clicked.connect(lambda: self.ltspice_converter.upload_file_LTspice(file_path_text_box.text()))
        button_layout.addWidget(upload_button)

        self.eConLayout.addLayout(button_layout)

        self.eConWidget.setLayout(self.eConLayout)

        # lib_path_text_box = QLineEdit()
        # lib_path_text_box.setFixedHeight(30)
        # lib_path_text_box.setFixedWidth(800)
        # lib_path_layout.setAlignment(Qt.AlignCenter)
        # lib_path_layout.addWidget(lib_path_text_box)

        # browse_button1 = QPushButton("Browse lib")
        # browse_button1.setFixedSize(110, 30)
        # browse_button1.clicked.connect(lambda: browse_path(self,lib_path_text_box))
        # lib_path_layout.addWidget(browse_button1)

        # self.eConLayout.addLayout(lib_path_layout)

        # Add the description HTML content
        description_html = """
            <html>
                <head>
                    <style>
                        body {
                            font-family: sans-serif;
                            margin: 0px;
                            padding: 0px;
                            background-color: white;
                            border: 4px solid  black;
                            font-size: 10pt; /* Adjust the font size as needed */
                        }

                        h1{
                            font-weight: bold;
                            font-size: 9pt;
                            color: #eeeeee;
                            padding: 10px;
                            background-color: #165982;
                            border: 4px outset  #0E324B;
                        }
                    </style>
                </head>

                <body>
                    <h1>About eSim Converter</h1>
                    <p>
                        <b>Pspice to eSim </b> will convert the PSpice Schematic and Library files to KiCad Schematic and
                        Library files respectively with proper mapping of the components and the wiring. By this way one 
                        will be able to simulate their schematics in PSpice and get the PCB layout in KiCad.</b> 
                        <br/><br/>
                        <b>LTspice to eSim </b> will convert symbols and schematics from LTspice to Kicad.The goal is to design and
                        simulate under LTspice and to automatically transfer the circuit under Kicad to draw the PCB.</b>
                    </p>
                </body>
            </html>
        """

        self.description_label = QLabel()
        self.description_label.setFixedHeight(160)
        self.description_label.setFixedWidth(950)
        self.description_label.setAlignment(Qt.AlignBottom)
        self.description_label.setWordWrap(True)
        self.description_label.setText(description_html)
        self.eConLayout.addWidget(self.description_label)  # Add the description label to the layout

        self.eConWidget.setLayout(self.eConLayout)

        dock[dockName + str(count)] = QtWidgets.QDockWidget(dockName + str(count))
        dock[dockName + str(count)].setWidget(self.eConWidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock[dockName + str(count)])
        self.tabifyDockWidget(dock['Welcome'], dock[dockName + str(count)])

        # CSS
        dock[dockName + str(count)].setStyleSheet(" \
            .QWidget { border-radius: 15px; border: 1px solid gray;\
                padding: 5px; width: 200px; height: 150px;  } \
            ")

        dock[dockName + str(count)].setVisible(True)
        dock[dockName + str(count)].setFocus()
        dock[dockName + str(count)].raise_()

        count = count + 1

    def modelEditor(self):
        """This function creates a widget for model editor."""
        global count

        self.modelwidget = QtWidgets.QWidget()
        self.modellayout = QtWidgets.QVBoxLayout()
        # Set smaller margins for the layout
        self.modellayout.setContentsMargins(4, 4, 4, 4)
        self.modellayout.setSpacing(4)
        self.modellayout.addWidget(ModelEditorclass())

        # Adding to main Layout
        self.modelwidget.setLayout(self.modellayout)
        dock['Model Editor-' + str(count)] = QtWidgets.QDockWidget('Model Editor-' + str(count))
        dock['Model Editor-' + str(count)].setWidget(self.modelwidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock['Model Editor-' + str(count)])
        self.tabifyDockWidget(dock['Welcome'], dock['Model Editor-' + str(count)])

        dock['Model Editor-' + str(count)].setVisible(True)
        dock['Model Editor-' + str(count)].setFocus()
        dock['Model Editor-' + str(count)].raise_()

        temp = self.obj_appconfig.current_project['ProjectName']
        if temp:
            self.obj_appconfig.dock_dict[temp].append(dock['Model Editor-' + str(count)])
        count = count + 1

    def kicadToNgspiceEditor(self, clarg1, clarg2=None):
        """
        This function is creating Editor UI for Kicad to Ngspice conversion.
        """
        global count

        projDir = self.obj_appconfig.current_project["ProjectName"]
        projName = os.path.basename(projDir)
        dockName = f'Netlist-{projName}-'

        self.kicadToNgspiceWidget = QtWidgets.QWidget()
        self.kicadToNgspiceLayout = QtWidgets.QVBoxLayout()
        self.kicadToNgspiceLayout.addWidget(MainWindow(clarg1, clarg2))

        self.kicadToNgspiceWidget.setLayout(self.kicadToNgspiceLayout)
        dock[dockName + str(count)] = \
            QtWidgets.QDockWidget(dockName + str(count))
        dock[dockName +
             str(count)].setWidget(self.kicadToNgspiceWidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                           dock[dockName + str(count)])
        self.tabifyDockWidget(dock['Welcome'],
                              dock[dockName + str(count)])

        # CSS
        dock[dockName + str(count)].setStyleSheet(" \
        .QWidget { border-radius: 15px; border: 1px solid gray;\
            padding: 5px; width: 200px; height: 150px;  } \
        ")

        dock[dockName + str(count)].setVisible(True)
        dock[dockName + str(count)].setFocus()
        dock[dockName + str(count)].raise_()
        dock[dockName + str(count)].activateWindow()

        temp = self.obj_appconfig.current_project['ProjectName']
        if temp:
            self.obj_appconfig.dock_dict[temp].append(
                dock[dockName + str(count)]
            )
        count = count + 1

    def subcircuiteditor(self):
        """This function creates a widget for different subcircuit options."""
        global count

        projDir = self.obj_appconfig.current_project["ProjectName"]

        """ Checks projDir variable has valid value 
        & is not None before calling os.path.basename """

        if projDir is not None:
            projName = os.path.basename(projDir)
            dockName = f'Subcircuit-{projName}-'

            self.subcktWidget = QtWidgets.QWidget()
            self.subcktLayout = QtWidgets.QVBoxLayout()
            self.subcktLayout.addWidget(Subcircuit(self))

            self.subcktWidget.setLayout(self.subcktLayout)
            dock[dockName +
                str(count)] = QtWidgets.QDockWidget(dockName
                                                    + str(count))
            dock[dockName + str(count)] \
                .setWidget(self.subcktWidget)
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                            dock[dockName + str(count)])
            self.tabifyDockWidget(dock['Welcome'],
                                dock[dockName + str(count)])

            # CSS
            dock[dockName + str(count)].setStyleSheet(" \
            .QWidget { border-radius: 15px; border: 1px solid gray;\
                padding: 5px; width: 200px; height: 150px;  } \
            ")

            dock[dockName + str(count)].setVisible(True)
            dock[dockName + str(count)].setFocus()
            dock[dockName + str(count)].raise_()

            count = count + 1

        else:
            """ when projDir is None that is clicking on subcircuit icon
                without any project selection """
            self.msg = QtWidgets.QErrorMessage()
            self.msg.setModal(True)
            self.msg.setWindowTitle("Error Message")
            self.msg.showMessage(
                'Please select the project first.'
                ' You can either create new project or open existing project'
            )
            self.msg.exec_()

    def makerchip(self):
        """This function creates a widget for different subcircuit options."""
        global count

        projDir = self.obj_appconfig.current_project["ProjectName"]
        if projDir is None:
            """ when projDir is None that is clicking on subcircuit icon
                without any project selection """
            self.msg = QtWidgets.QErrorMessage()
            self.msg.setModal(True)
            self.msg.setWindowTitle("Error Message")
            self.msg.showMessage(
                'Please select the project first.'
                ' You can either create new project or open existing project'
            )
            self.msg.exec_()
            return
        projName = os.path.basename(projDir)
        dockName = f'Makerchip-{projName}-'

        self.makerWidget = QtWidgets.QWidget()
        self.makerLayout = QtWidgets.QVBoxLayout()
        self.makerLayout.addWidget(makerchip(self))

        self.makerWidget.setLayout(self.makerLayout)
        dock[dockName +
             str(count)] = QtWidgets.QDockWidget(dockName
                                                 + str(count))
        dock[dockName + str(count)].setWidget(self.makerWidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                           dock[dockName + str(count)])
        self.tabifyDockWidget(dock['Welcome'],
                              dock[dockName + str(count)])

        # CSS
        dock[dockName + str(count)].setStyleSheet(" \
        .QWidget { border-radius: 15px; border: 1px solid gray;\
            padding: 5px; width: 200px; height: 150px;  } \
        ")

        dock[dockName + str(count)].setVisible(True)
        dock[dockName + str(count)].setFocus()
        dock[dockName + str(count)].raise_()

        count = count + 1

    def usermanual(self):
        """This function creates a widget for user manual."""
        global count
        self.usermanualWidget = QtWidgets.QWidget()
        self.usermanualLayout = QtWidgets.QVBoxLayout()
        self.usermanualLayout.addWidget(UserManual())

        self.usermanualWidget.setLayout(self.usermanualLayout)
        dock['User Manual-' +
             str(count)] = QtWidgets.QDockWidget('User Manual-' + str(count))
        dock['User Manual-' + str(count)].setWidget(self.usermanualWidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                           dock['User Manual-' + str(count)])
        self.tabifyDockWidget(dock['Welcome'],
                              dock['User Manual-' + str(count)])

        # CSS
        dock['User Manual-' + str(count)].setStyleSheet(" \
        .QWidget { border-radius: 15px; border: 1px solid gray;\
            padding: 5px; width: 200px; height: 150px;  } \
        ")

        dock['User Manual-' + str(count)].setVisible(True)
        dock['User Manual-' + str(count)].setFocus()
        dock['User Manual-' + str(count)].raise_()

        count = count + 1

    def modelicaEditor(self, projDir):
        """This function sets up the UI for ngspice to modelica conversion."""
        global count

        projName = os.path.basename(projDir)
        dockName = f'Modelica-{projName}-'

        self.modelicaWidget = QtWidgets.QWidget()
        self.modelicaLayout = QtWidgets.QVBoxLayout()
        self.modelicaLayout.addWidget(OpenModelicaEditor(projDir))

        self.modelicaWidget.setLayout(self.modelicaLayout)
        dock[dockName + str(count)
             ] = QtWidgets.QDockWidget(dockName + str(count))
        dock[dockName + str(count)] \
            .setWidget(self.modelicaWidget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                           dock[dockName
                                + str(count)])
        self.tabifyDockWidget(dock['Welcome'], dock[dockName
                                                    + str(count)])

        dock[dockName + str(count)].setVisible(True)
        dock[dockName + str(count)].setFocus()
        dock[dockName + str(count)].raise_()

        # CSS
        dock[dockName + str(count)].setStyleSheet(" \
        .QWidget { border-radius: 15px; border: 1px solid gray;\
            padding: 5px; width: 200px; height: 150px;  } \
        ")
        temp = self.obj_appconfig.current_project['ProjectName']
        if temp:
            self.obj_appconfig.dock_dict[temp].append(
                dock[dockName + str(count)]
            )

        count = count + 1

    def closeDock(self):
        """
        This function checks for the project in **dock_dict**
        and closes it.
        """
        self.temp = self.obj_appconfig.current_project['ProjectName']
        for dockwidget in self.obj_appconfig.dock_dict[self.temp]:
            dockwidget.close()