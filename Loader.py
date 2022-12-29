import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QDialog
from Project import Console
from PyQt5.QtCore import pyqtSlot
import resource


class GUI(QDialog):
    """
    Constructor of GUI class
    """
    def __init__(self):
        super(GUI, self).__init__()
        loadUi("loading.ui", self)
        self.console = None
        self.runButton.clicked.connect(self.Run)

    @pyqtSlot()
    def Run(self):
        """
        loads the console window
        and runs it
        :return:
        """
        ui.hide()
        self.console = Console()
        self.console.show()
        self.console.beginDetection()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = GUI()
    ui.show()
    sys.exit(app.exec_())
