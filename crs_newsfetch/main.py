import sys
from PySide6 import QtWidgets

from gui import Gui

def main():
    app = QtWidgets.QApplication([])
    gui = Gui()
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
