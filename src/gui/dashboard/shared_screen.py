from dataclasses import dataclass
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from src.service.share import get_shared_with_me

@dataclass
class SharedScreen(QWidget):
    owner: QTabWidget
    btn_refresh_share: QPushButton

    def __init__(self, owner: QTabWidget):
        QWidget.__init__(self)
        self.owner = owner

        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.btn_refresh_share = QPushButton("Refresh")
        self.btn_refresh_share.clicked.connect(self.on_click_refresh)

    def make_layout(self):
        layout_main = QVBoxLayout()
        layout_top_bar = QHBoxLayout()
        layout_table_edit = QHBoxLayout()

        layout_main.addLayout(layout_top_bar)
        layout_main.addLayout(layout_table_edit)
        
        layout_top_bar.addWidget(self.btn_refresh_share)
        self.setLayout(layout_main)

    def on_click_refresh(self):
        self.reload_shared()

    def reload_shared(self):
        get_shared_with_me()