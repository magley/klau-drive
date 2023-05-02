from dataclasses import dataclass
from PyQt6.QtWidgets import *
from src.lambdas.login import login, NoSuchUserException
from src.gui.common import show_error
import src.gui.gui_window as mainWindow
import src.gui.token_util as token_util


@dataclass
class LoginScreen(QWidget):
    # TODO: Declare other fields.
    btn_login: QPushButton
    btn_register: QPushButton
    btn_admin: QPushButton
    owner: QStackedWidget
    txt_username: QLineEdit
    txt_password: QLineEdit

    def __init__(self, owner: QStackedWidget):
        QWidget.__init__(self)
        self.owner = owner
        
        self.init_gui()
        self.make_layout()

    def init_gui(self):
        # TODO: Initialize other fields.

        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.on_login_clicked)
        self.btn_admin = QPushButton("I'm an admin")
        self.btn_admin.clicked.connect(self.on_admin_clicked)
        self.btn_register = QPushButton("Register")
        self.btn_register.clicked.connect(self.on_register_clicked)
        self.txt_username = QLineEdit()
        self.txt_password = QLineEdit()

    def make_layout(self):
        layout_main = QVBoxLayout()

        login_form = QFormLayout()
        login_form.addRow(QLabel("Username"), self.txt_username)
        login_form.addRow(QLabel("Password"), self.txt_password)
        login_form.addRow(self.btn_login)
        layout_main.addLayout(login_form)

        layout_main.addItem(QSpacerItem(
            1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout_main.addWidget(self.btn_register)
        layout_main.addWidget(self.btn_admin)

        self.setLayout(layout_main)

    def on_login_clicked(self):
        username = self.txt_username.text()
        if username == "":
            show_error("Username cannot be empty.")
            return
        password = self.txt_password.text()
        if password == "":
            show_error("Password cannot be empty.")
            return
        self.do_login(username, password)

    def on_admin_clicked(self):
        self.do_login("admin", "admin")

    def do_login(self, username, password):
        try:
            jwt = login(username, password)
        except NoSuchUserException as e:
            show_error(str(e))
            return
        else:
            token_util.write_token(jwt)
            print("Logged in: " + token_util.read_token())
        self.owner.setCurrentIndex(mainWindow.MainWindow.SCREEN_DASHBOARD)

    def on_register_clicked(self):
        self.owner.setCurrentIndex(mainWindow.MainWindow.SCREEN_REGISTER)


