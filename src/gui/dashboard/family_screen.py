from dataclasses import dataclass
from typing import List
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from src.service.family import approve, get_family_verifications, reject


@dataclass
class FamilyScreen(QWidget):
    owner: QTabWidget
    btn_refresh: QPushButton
    btn_approve: QPushButton
    btn_reject: QPushButton
    table: QTableWidget
    items: List
    columns: List[str]

    selected_item: object = None

    def __init__(self, owner: QTabWidget):
        QWidget.__init__(self)
        self.owner = owner

        self.items = []
        self.columns = ["sharing_to_username"]

        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.on_click_refresh)

        self.btn_approve = QPushButton("Approve sharing")
        self.btn_approve.clicked.connect(self.on_click_approve_sharing)

        self.btn_reject = QPushButton("Reject sharing")
        self.btn_reject.clicked.connect(self.on_click_reject_sharing)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.setColumnWidth(0, 450)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.clicked.connect(self.on_click_item)

        self.btn_approve.setEnabled(False)
        self.btn_reject.setEnabled(False)

    def make_layout(self):
        layout_main = QVBoxLayout()
        layout_top_bar = QHBoxLayout()
        layout_table_edit = QHBoxLayout()

        layout_main.addLayout(layout_top_bar)
        layout_main.addLayout(layout_table_edit)

        layout_table_edit.addWidget(self.table)

        layout_top_bar.addWidget(self.btn_refresh)
        layout_top_bar.addWidget(self.btn_approve)
        layout_top_bar.addWidget(self.btn_reject)
        self.setLayout(layout_main)

    def on_click_refresh(self):
        self.reload_family()

    def reload_family(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        self.items.clear()
        self.table.clearContents()

        self.items = get_family_verifications()
        self.table.setRowCount(len(self.items))

        for row, item in enumerate(self.items):
            self.table.setItem(row, 0, QTableWidgetItem(item["sharing_to_username"]))
            self.table.setRowHeight(row, 8)
        QApplication.restoreOverrideCursor()

    def on_click_item(self, item: QModelIndex):
        self.selected_item = self.items[item.row()]
        self.btn_approve.setEnabled(True)
        self.btn_reject.setEnabled(True)

    def on_click_approve_sharing(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        approve(self.selected_item["sharing_to_username"])
        QApplication.restoreOverrideCursor()
        self.btn_approve.setEnabled(False)
        self.reload_family()

    def on_click_reject_sharing(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        reject(self.selected_item["sharing_to_username"])
        QApplication.restoreOverrideCursor()
        self.btn_reject.setEnabled(False)
        self.reload_family()
