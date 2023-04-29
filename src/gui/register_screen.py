from PyQt6.QtWidgets import *
from src.lambdas.register_user import User, register_user
from datetime import datetime, date

class RegisterScreen(QWidget):
    def __init__(self, win: QStackedWidget):
        QWidget.__init__(self)
        self.win = win
        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.txt_name = QLineEdit()
        self.txt_surname = QLineEdit()
        self.txt_date_of_birth = QLineEdit()
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
        layout.addRow(QLabel('Date of birth'), self.txt_date_of_birth)
        layout.addRow(QLabel('Username'), self.txt_username)
        layout.addRow(QLabel('Email'), self.txt_email)
        layout.addRow(QLabel('Password'), self.txt_password)
        layout.addRow(self.btn_register)
        self.setLayout(layout)

    def on_register_clicked(self):
        dob, err = self.attempt_dob_parse()
        if err:
            self.show_error('Date of birth format invalid.\nProper format is dd-mm-YYYY')
            return
        username = self.txt_username.text()
        if username == '':
            self.show_error('Username cannot be empty.')
            return
        user = User(
            name=self.txt_name.text(),
            surname=self.txt_surname.text(),
            date_of_birth=dob,
            username=username,
            email=self.txt_email.text(),
            password=self.txt_password.text()
        )
        err = register_user(user)
        if err:
            self.show_error(err)
            return
        self.show_success()

    def attempt_dob_parse(self) -> tuple[date | None, bool]:
        dob_text = self.txt_date_of_birth.text()
        if dob_text == '':
            return None, False
        try:    
            dob = datetime.strptime(dob_text, '%d-%m-%Y').date()
            return dob.strftime('%d-%m-%Y'), False
        except ValueError:
            return None, True

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
