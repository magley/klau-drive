from typing import List
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class OverviewScreen(QWidget):
    def __init__(self, parent: QTabWidget):
        QWidget.__init__(self)
        self.parent = parent

        self.files: List = ['a', 'b', 'c']
        self.mdl_files: QStandardItemModel = None
        self.lst_files: QListView = None

        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.lst_files = QListView()
        self.mdl_files = QStandardItemModel()
        self.lst_files.setModel(self.mdl_files)

        for item in self.files:
            self.mdl_files.appendRow(QStandardItem(item))

    def make_layout(self):
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.lst_files)
        self.setLayout(layout_main)