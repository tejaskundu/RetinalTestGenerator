import sys
import View
from PyQt5.QtWidgets import QApplication
import os


if __name__ == '__main__':

    app = QApplication(sys.argv)
    interface = View.MainQtWindow(app.primaryScreen().size().width(), app.primaryScreen().size().height())
    sys.exit(app.exec_())

