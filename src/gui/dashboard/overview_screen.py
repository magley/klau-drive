from typing import List
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from src.lambdas.upload_file import list_files, FileData

class OverviewScreen(QWidget):
    def __init__(self, parent: QTabWidget):
        QWidget.__init__(self)
        self.parent = parent

        self.table: QTableWidget
        self.files: List[FileData] = []
        self.columns = ['Icon', 'Name', 'Type', 'Date Modified']

        self.init_gui()
        self.make_layout()

        self.refresh()

    def init_gui(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)


    def make_layout(self):
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.table)
        self.setLayout(layout_main)

    def refresh(self):
        self.files.clear()

    def refresh(self):
        self.load_files_from_cloud()

    def load_files_from_cloud(self):
        self.clear_list()

        self.files = list_files()
        self.table.setRowCount(len(self.files))

        for row, file in enumerate(list_files()):
            file: FileData = file
            self.put_file_in_table(file, row)

    def clear_list(self):
        self.files.clear()
        self.table.clearContents()
        
    def put_file_in_table(self, file: FileData, row: int):
        pixmapi = QStyle.StandardPixmap.SP_FileIcon
        icon = self.style().standardIcon(pixmapi)
        icon_item = QTableWidgetItem()
        icon_item.setIcon(icon)

        self.table.setItem(row, 0, QTableWidgetItem(icon_item))
        self.table.setItem(row, 1, QTableWidgetItem(file.name))
        self.table.setItem(row, 2, QTableWidgetItem(file.type))
        self.table.setItem(row, 3, QTableWidgetItem(file.last_modified.strftime('%a %d %b %Y, %I:%M%p')))