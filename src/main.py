from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from src.gui.upload_screen import UploadScreen


app = QApplication([])
app.setStyle('Windows') # Fusion

main_window = QStackedWidget()
main_window.resize(640, 480)
main_window.setWindowTitle('klau-drive')
main_window.addWidget(UploadScreen(main_window))
main_window.setWindowIcon(QtGui.QIcon('res/ico.png'))

main_window.show()

app.exec()