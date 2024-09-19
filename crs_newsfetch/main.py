import sys
import PySide6

from gui import Gui

def main():
    app = PySide6.QtWidgets.QApplication([])
    gui = Gui()
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
