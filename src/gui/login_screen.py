from PyQt6.QtWidgets import *
import src.gui.gui_window as mainWindow


class LoginScreen(QWidget):
    def __init__(self, win: QStackedWidget):
        QWidget.__init__(self)
        self.win = win

        # TODO: Declare other fields.
        self.btn_login: QPushButton


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
        layout_main.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout_main)


    def on_login_clicked(self):
        # TODO: Add logic.

        self.win.setCurrentIndex(mainWindow.MainWindow.SCREEN_DASHBOARD)