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
                <style type="text/css">
                    body {
                        background-color: #23273a;
                        color: #e8eaed;
                    }
                    a, a:link, a:visited, a:hover, a:active {
                        color: #40c4ff !important;
                    }
                    .tableofcontents span, h1, h2, h3, h4, h5, h6,
                    .likechapterHead, .chapterHead, .sectionHead, .subsectionHead,
                    .cmbx-12x-x-207, .cmbx-12x-x-144, .cmr-10, .cmbx-10, .cmti-10x-x-109, .cmtt-10x-x-109 {
                         color: #e8eaed !important;
                    }
                </style>
                """
                # Inject styles into the head of the document
                html_content = html_content.replace('</head>', dark_style + '</head>')

            self.browser.setHtml(html_content)
                
            # Set base URL to help browser find images
            self.browser.setSearchPaths([os.path.dirname(path_from_script)])

        except FileNotFoundError:
            self.browser.setText("Error: User manual file not found at " + os.path.realpath(path_from_script))

        self.browser.setOpenExternalLinks(True)

        self.vlayout.addWidget(self.browser)
        self.setLayout(self.vlayout)
        self.show()
