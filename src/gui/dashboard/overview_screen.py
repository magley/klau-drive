from PyQt6.QtWidgets import *

class OverviewScreen(QWidget):
    def __init__(self, parent: QTabWidget):
        QWidget.__init__(self)
        self.parent = parent