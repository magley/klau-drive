from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from src.gui.login_screen import LoginScreen
from src.gui.dashboard_screen import DashboardScreen
from src.gui.register_screen import RegisterScreen

class MainWindow(QStackedWidget):
    SCREEN_LOGIN = 0
    SCREEN_REGISTER = 1
    SCREEN_DASHBOARD = 2

    def __init__(self, width, height):
        QStackedWidget.__init__(self)

        self.resize(width, height)
        self.setWindowTitle('klau-drive')
        self.setWindowIcon(QtGui.QIcon('res/ico.png'))

        MainWindow.SCREEN_REGISTER = self.addWidget(RegisterScreen(self))
        MainWindow.SCREEN_LOGIN = self.addWidget(LoginScreen(self))
        MainWindow.SCREEN_DASHBOARD = self.addWidget(DashboardScreen(self))
