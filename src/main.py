from PyQt6.QtWidgets import *
from src.gui.gui_window import MainWindow

app = QApplication([])
app.setStyle('Fusion')  # 'Fusion'

main_window = MainWindow(640, 480)
main_window.show()

app.exec()
