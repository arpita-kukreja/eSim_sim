# =========================================================================
#             FILE: makerchip.py
#
#            USAGE: ---
#
#      DESCRIPTION: This defines all components of the Makerchip.
#
#          OPTIONS: ---
#     REQUIREMENTS: ---
#             BUGS: ---
#            NOTES: ---
#           AUTHOR: Sumanto Kar, sumantokar@iitb.ac.in, FOSSEE, IIT Bombay
# ACKNOWLEDGEMENTS: Rahul Paknikar, rahulp@iitb.ac.in, FOSSEE, IIT Bombay
#                Digvijay Singh, digvijay.singh@iitb.ac.in, FOSSEE, IIT Bombay
#                Prof. Maheswari R. and Team, VIT Chennai
#     GUIDED BY: Steve Hoover, Founder Redwood EDA
#                Kunal Ghosh, VLSI System Design Corp.Pvt.Ltd
#                Anagha Ghosh, VLSI System Design Corp.Pvt.Ltd
# OTHER CONTRIBUTERS:
#                Prof. Madhuri Kadam, Shree L. R. Tiwari College of Engineering
#                Rohinth Ram, Madras Institue of Technology
#                Charaan S., Madras Institue of Technology
#                Nalinkumar S., Madras Institue of Technology
#  ORGANIZATION: eSim Team at FOSSEE, IIT Bombay
#       CREATED: Monday 29, November 2021
#      REVISION: Tuesday 25, January 2022
# =========================================================================

# importing the files and libraries
from PyQt5 import QtWidgets
from . import Maker
from . import NgVeri

# filecount is used to count thenumber of objects created
filecount = 0


# This class creates objects for creating the Maker and the Ngveri tabs
class makerchip(QtWidgets.QWidget):

    # initialising the variables
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)

        # filecount=int(open("a.txt",'r').read())
        print(filecount)
        # self.splitter.setOrientation(QtCore.Qt.Vertical)
        print("==================================")
        print("Makerchip and Verilog to Ngspice Converter")
        print("==================================")
        self.createMainWindow()

    # Creating the main Window(Main tab)

    def createMainWindow(self):
        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addStretch(1)
        self.vbox.addWidget(self.createWidget())
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)
        self.setWindowTitle("Makerchip and Verilog to Ngspice Converter")
        self.show()

    # Creating the maker and ngveri widgets
    def createWidget(self):
        global obj_Maker
        global filecount
        self.convertWindow = QtWidgets.QWidget()

        # Apply dark theme to the main window
        self.convertWindow.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
            }
            QTabWidget::pane {
                border: 2px solid #23273a;
                border-radius: 14px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #23273a, stop:1 #181b24);
                color: #e8eaed;
                border: 1px solid #40c4ff;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 25px;
                margin-right: 2px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #40c4ff, stop:1 #1976d2);
                color: #181b24;
                border: 1px solid #40c4ff;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background: #1976d2;
                color: #fff;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #23273a;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #40c4ff;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            /* Text Area Styling */
            QTextEdit, QPlainTextEdit {
                background: #1a1d2a;
                color: #e8eaed;
                border: 2px solid #40c4ff;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                selection-background-color: #1976d2;
                border: 2px solid #1976d2;
                selection-color: #ffffff;
                
            }
            QTextEdit:focus, QPlainTextEdit:focus {
                border: 2px solid #1976d2;
                background: #1e2132;
            }
            /* Input Field Styling */
            QLineEdit {
                background: #1a1d2a;
                color: #e8eaed;
                border: 2px solid #40c4ff;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #1976d2;
                background: #1e2132;
            }
            /* Code Input Section */
            .tiv-code {
                background: #1e2132;
                border: 2px solid #1976d2;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            /* Group Box Styling */
            QGroupBox {
                background: #1a1d2a;
                border: 2px solid #40c4ff;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #40c4ff;
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)

        self.MakerTab = QtWidgets.QScrollArea()
        obj_Maker = Maker.Maker(filecount)
        self.MakerTab.setWidget(obj_Maker)
        self.MakerTab.setWidgetResizable(True)

        global obj_NgVeri
        self.NgVeriTab = QtWidgets.QScrollArea()
        obj_NgVeri = NgVeri.NgVeri(filecount)
        self.NgVeriTab.setWidget(obj_NgVeri)
        self.NgVeriTab.setWidgetResizable(True)

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.addTab(self.MakerTab, "Makerchip")
        self.tabWidget.addTab(self.NgVeriTab, "NgVeri")
        
        # The object refresh gets destroyed when Ngspice to verilog converter is called
        # so calling refresh_change to start toggling of refresh again
        self.tabWidget.currentChanged.connect(obj_Maker.refresh_change)
        
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(15, 15, 15, 15)  # Add margins
        self.mainLayout.setSpacing(15)  # Add spacing
        self.mainLayout.addWidget(self.tabWidget)
        
        self.convertWindow.setLayout(self.mainLayout)
        self.convertWindow.show()
        
        # incrementing filecount for every new window
        filecount = filecount + 1
        return self.convertWindow
