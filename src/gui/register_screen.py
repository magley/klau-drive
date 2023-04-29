from PyQt6.QtWidgets import *
from src.lambdas.register_user import User, register_user, list_users
from datetime import datetime
import src.gui.gui_window as mainWindow

class RegisterScreen(QWidget):
    def __init__(self, owner: QStackedWidget):
        QWidget.__init__(self)
        self.owner = owner
        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.txt_name = QLineEdit()
        self.txt_surname = QLineEdit()
        self.date_of_birth = QDateEdit(calendarPopup=True)
        self.txt_username = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_register = QPushButton('Register')
        self.btn_register.clicked.connect(self.on_register_clicked)

    def make_layout(self):
        layout = QFormLayout()
        layout.addRow(QLabel('Name'), self.txt_name)
        layout.addRow(QLabel('Surname'), self.txt_surname)
        layout.addRow(QLabel('Date of birth'), self.date_of_birth)
        layout.addRow(QLabel('Username'), self.txt_username)
        layout.addRow(QLabel('Email'), self.txt_email)
        layout.addRow(QLabel('Password'), self.txt_password)
        layout.addRow(self.btn_register)
        self.setLayout(layout)

    def on_register_clicked(self):
        dob = self.date_of_birth.dateTime().toPyDateTime()
        if dob > datetime.now():
            self.show_error('Date of birth cannot be a future date.')
            return

        username = self.txt_username.text()
        if username == '':
            self.show_error('Username cannot be empty.')
            return

        password = self.txt_password.text()
        if password == '':
            self.show_error('Password cannot be empty.')
            return

        user = User(
            name=self.txt_name.text(),
            surname=self.txt_surname.text(),
            date_of_birth=dob,
            username=username,
            email=self.txt_email.text(),
            password=password
        )
        err = register_user(user)
        if err:
            self.show_error(err)
            return

        list_users()
        self.show_success()
        # self.owner.setCurrentIndex(mainWindow.MainWindow.SCREEN_DASHBOARD)


    def show_error(self, error):
        msg = QMessageBox()
        msg.setWindowTitle('Error')
        msg.setText(error)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def show_success(self):
        msg = QMessageBox()
        msg.setWindowTitle('Success')
        msg.setText('Successfully registered user.')
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
