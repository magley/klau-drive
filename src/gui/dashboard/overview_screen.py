from typing import List
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from src.lambdas.upload_file import list_files, FileData

class OverviewScreen(QWidget):
    def __init__(self, parent: QTabWidget):
        QWidget.__init__(self)
        self.parent = parent

        self.files: List = ['a', 'b', 'c']
        self.mdl_files: QStandardItemModel = None
        self.lst_files: QListView = None

        self.init_gui()
        self.make_layout()

        self.refresh()

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

    def refresh(self):
        self.load_files_from_cloud()

    def load_files_from_cloud(self):
        self.clear_list()

        for file in list_files():
            file: FileData = file
            self.add_to_list(file)

    def clear_list(self):
        self.files.clear()
        self.mdl_files.clear()

    def add_to_list(self, file: FileData):
        self.files.append(str(file))

        mdl_item = QStandardItem(str(file))
        
        pixmapi = QStyle.StandardPixmap.SP_FileIcon
        icon = self.style().standardIcon(pixmapi)
        mdl_item.setIcon(icon)

        self.mdl_files.appendRow(mdl_item)