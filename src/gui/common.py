from PyQt6.QtWidgets import *


def show_error(error):
    msg = QMessageBox()
    msg.setWindowTitle('Error')
    msg.setText(error)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


def show_success(text):
    msg = QMessageBox()
    msg.setWindowTitle('Success')
    msg.setText(text)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()
