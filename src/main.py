from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from src.gui.gui_window import MainWindow

app = QApplication([])
app.setStyle('Fusion')  # 'Fusion'

# TODO[LOGIN_ISSUES]
import os
try:
    os.remove("./user_token.txt")
except:
    pass

main_window = MainWindow(640, 480)
main_window.show()


app.exec()
