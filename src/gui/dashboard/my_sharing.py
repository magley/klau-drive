from dataclasses import dataclass
from typing import List
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from src.service.share import get_my_sharing, stop_share

@dataclass
class MySharingScreen(QWidget):
    owner: QTabWidget
    btn_refresh_share: QPushButton
    btn_stop_share: QPushButton
    table: QTableWidget
    items: List
    columns: List[str]

    selected_item: object = None

    def __init__(self, owner: QTabWidget):
        QWidget.__init__(self)
        self.owner = owner

        self.items = []
        self.columns = ['uuid', 'folder', 'sharing with']

        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.btn_refresh_share = QPushButton("Refresh")
        self.btn_refresh_share.clicked.connect(self.on_click_refresh)

        self.btn_stop_share = QPushButton("Stop sharing")
        self.btn_stop_share.clicked.connect(self.on_click_stop_share)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.clicked.connect(self.on_click_item)

        self.btn_stop_share.setEnabled(False)

    def make_layout(self):
        layout_main = QVBoxLayout()
        layout_top_bar = QHBoxLayout()
        layout_table_edit = QHBoxLayout()

        layout_main.addLayout(layout_top_bar)
        layout_main.addLayout(layout_table_edit)

        layout_table_edit.addWidget(self.table)
        
        layout_top_bar.addWidget(self.btn_refresh_share)
        layout_top_bar.addWidget(self.btn_stop_share)
        self.setLayout(layout_main)

    def on_click_refresh(self):
        self.reload_shared()

    def reload_shared(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        self.items.clear()
        self.table.clearContents()

        self.items = get_my_sharing()
        self.table.setRowCount(len(self.items))

        for row, item in enumerate(self.items):       
            self.table.setItem(row, 0, QTableWidgetItem(item['uuid']))
            self.table.setItem(row, 1, QTableWidgetItem(item['type']))
            self.table.setItem(row, 2, QTableWidgetItem(item['username']))

            self.table.setRowHeight(row, 8)
        QApplication.restoreOverrideCursor()

        get_my_sharing()

    def on_click_item(self, item: QModelIndex):
        self.selected_item = self.items[item.row()]
        self.btn_stop_share.setEnabled(True)

    def on_click_stop_share(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        stop_share(self.selected_item['owner'], self.selected_item['uuid'], self.selected_item['username'])
        QApplication.restoreOverrideCursor()

        self.btn_stop_share.setEnabled(False)