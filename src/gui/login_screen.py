from dataclasses import dataclass
from PyQt6.QtWidgets import *
import src.gui.gui_window as mainWindow


@dataclass
class LoginScreen(QWidget):
    # TODO: Declare other fields.
    btn_login: QPushButton
    owner: QStackedWidget

    def __init__(self, owner: QStackedWidget):
        QWidget.__init__(self)
        self.owner = owner
        
        self.init_gui()
        self.make_layout()

    def init_gui(self):
        # TODO: Initialize other fields.

        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.on_login_clicked)

    def make_layout(self):
        # TODO: Add other fields to layout.
        layout_main = QVBoxLayout()

        layout_main.addWidget(self.btn_login)
        layout_main.addItem(QSpacerItem(
            1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout_main)

    def on_login_clicked(self):
        # TODO: Add logic.

        self.owner.setCurrentIndex(mainWindow.MainWindow.SCREEN_DASHBOARD)
