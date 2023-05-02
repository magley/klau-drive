from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from src.gui.login_screen import LoginScreen
from src.gui.dashboard_screen import DashboardScreen
from src.gui.register_screen import RegisterScreen
import src.gui.token_util as token_util


class MainWindow(QMainWindow):
    SCREEN_LOGIN = 0
    SCREEN_REGISTER = 1
    SCREEN_DASHBOARD = 2

    def __init__(self, width, height, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.resize(width, height)
        self.setWindowTitle('klau-drive')
        self.setWindowIcon(QtGui.QIcon('res/ico.png'))
        self.stack_widget = QStackedWidget(self)
        self.setCentralWidget(self.stack_widget)

        menu_bar = self.menuBar()
        file_menu: QMenu = menu_bar.addMenu("&File")
        logout_action = QAction("Logout", self)
        file_menu.addAction(logout_action)
        logout_action.triggered.connect(self.logout_clicked)

        MainWindow.SCREEN_LOGIN = self.stack_widget.addWidget(LoginScreen(self.stack_widget))
        MainWindow.SCREEN_REGISTER = self.stack_widget.addWidget(RegisterScreen(self.stack_widget))
        MainWindow.SCREEN_DASHBOARD = self.stack_widget.addWidget(DashboardScreen(self.stack_widget))

    def logout_clicked(self):
        token_util.delete_token()
        self.stack_widget.setCurrentIndex(MainWindow.SCREEN_LOGIN)
