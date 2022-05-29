
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
import resource
from out_window import Ui_OutputDialog

#to open and load main window
class Ui_Dialog(QDialog):
    def __init__(self):
        super(Ui_Dialog, self).__init__()
        loadUi("mainwindow.ui", self)

        self.runButton.clicked.connect(self.runSlot)

        self._new_window = None
        self.Videocapture_ = None

    def refreshAll(self):

        self.Videocapture_ = "0"
    # to open output window when user clicks start button
    @pyqtSlot()
    def runSlot(self):

        print("Clicked Run")
        self.refreshAll()
        print(self.Videocapture_)
        # hide the main window
        ui.hide()
        # Create and open new output window
        self.outputWindow_()
    # to switch on camera when output window is opened
    def outputWindow_(self):

        self._new_window = Ui_OutputDialog()
        self._new_window.show()
        self._new_window.startVideo(self.Videocapture_)
        print("Video Played")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_Dialog()
    ui.show()
    sys.exit(app.exec_())
