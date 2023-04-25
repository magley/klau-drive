from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from src.gui.gui_window import MainWindow

from src.lambdas.upload_file import init
init()

app = QApplication([])
app.setStyle('Fusion')  # 'Fusion'

main_window = MainWindow(640, 480)
main_window.show()


app.exec()