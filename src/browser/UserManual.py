from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPalette, QColor
import os


class UserManual(QtWidgets.QWidget):
    """
    This class displays the user manual in a widget.
    """

    def __init__(self, is_dark_theme=False):
        QtWidgets.QWidget.__init__(self)

        self.vlayout = QtWidgets.QVBoxLayout()
        self.browser = QtWidgets.QTextBrowser()

        path_from_script = os.path.join(os.path.dirname(__file__), '..', '..', 'library', 'browser', 'User-Manual', 'eSim.html')

        try:
            with open(path_from_script, 'r', encoding='utf-8') as f:
                html_content = f.read()

            if is_dark_theme:
                dark_style = """
                <style>
                    body {
                        background-color: #2e2e2e;
                        color: #ffffff;
                    }
                    a {
                        color: #56a8d8;
                    }
                    .tableofcontents span {
                        color: #ffffff !important;
                    }
                </style>
                """
                html_content = dark_style + html_content

            self.browser.setHtml(html_content)
                
            # Set base URL to help browser find images
            self.browser.setSearchPaths([os.path.dirname(path_from_script)])

        except FileNotFoundError:
            self.browser.setText("Error: User manual file not found at " + os.path.realpath(path_from_script))

        self.browser.setOpenExternalLinks(True)

        self.vlayout.addWidget(self.browser)
        self.setLayout(self.vlayout)
        self.show()
