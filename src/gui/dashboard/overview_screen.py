from typing import List
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from src.lambdas.upload_file import list_files, FileData

class FileEdit(QGroupBox):
    def __init__(self, parent: "OverviewScreen"):
        QGroupBox.__init__(self)
        self.owner = parent

        self.txt_name: QLineEdit
        self.txt_desc: QTextEdit
        self.btn_update: QPushButton
        self.lbl_upload_date: QLabel
        self.lbl_modify_date: QLabel
        self.lbl_size: QLabel

        self.init_gui()
        self.init_layout()

    def init_gui(self):
        self.txt_name = QLineEdit()
        self.txt_desc = QTextEdit()
        self.lbl_upload_date = QLabel()
        self.lbl_modify_date = QLabel()
        self.lbl_size = QLabel()
        self.btn_update = QPushButton("Save Changes")

    def init_layout(self):
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.txt_name)
        layout_main.addWidget(self.txt_desc)
        layout_main.addWidget(self.lbl_size)
        layout_main.addWidget(self.lbl_upload_date)
        layout_main.addWidget(self.lbl_modify_date)

        layout_main.addWidget(self.btn_update)
        layout_main.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout_main)

    def on_selected_file(self, file: FileData):
        self.txt_name.setText(file.name)
        self.txt_desc.setText(file.desc)
        
        self.lbl_size.setText(f"{file.size} B")
        self.lbl_upload_date.setText(file.upload_date.strftime('%a %d %b %Y, %I:%M%p'))
        self.lbl_modify_date.setText(file.last_modified.strftime('%a %d %b %Y, %I:%M%p'))


class OverviewScreen(QWidget):
    def __init__(self, parent: QTabWidget):
        QWidget.__init__(self)
        self.owner = parent

        self.table: QTableWidget
        self.edit_region: FileEdit
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
        self.table.setShowGrid(False)
        self.table.clicked.connect(self.on_click_item)

        self.edit_region = FileEdit(self)

    def make_layout(self):
        layout_main = QHBoxLayout()
        
        hsplitter = QSplitter(Qt.Orientation.Horizontal)
        hsplitter.addWidget(self.table)
        hsplitter.addWidget(self.edit_region)

        layout_main.addWidget(hsplitter)

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
            self.table.setRowHeight(row, 8)

    def clear_list(self):
        self.files.clear()
        self.table.clearContents()
        
    def put_file_in_table(self, file: FileData, row: int):
        pixmapi = QStyle.StandardPixmap.SP_FileIcon
        icon = self.style().standardIcon(pixmapi)
        icon_item = QTableWidgetItem()
        icon_item.setIcon(icon)

        self.table.setItem(row, 0, QTableWidgetItem(icon_item))
        self.table.setItem(row, 1, QTableWidgetItem(file.name + file.type))
        self.table.setItem(row, 2, QTableWidgetItem(file.type))
        self.table.setItem(row, 3, QTableWidgetItem(file.last_modified.strftime('%a %d %b %Y, %I:%M%p')))

    def on_click_item(self, item: QModelIndex):
        self.edit_region.on_selected_file(self.files[item.row()])