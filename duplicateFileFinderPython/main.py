import FileFinderGui as gui
import sys
from PyQt5 import Qt

if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    ex = gui.FileFinderGui()
    sys.exit(app.exec_())