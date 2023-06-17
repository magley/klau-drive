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
        self.logout_action = QAction("&Logout", self)
        file_menu.addAction(self.logout_action)
        self.logout_action.triggered.connect(self.logout_clicked)
        self.stack_widget.currentChanged.connect(self.page_change)

        MainWindow.SCREEN_LOGIN = self.stack_widget.addWidget(LoginScreen(self.stack_widget))
        MainWindow.SCREEN_REGISTER = self.stack_widget.addWidget(RegisterScreen(self.stack_widget))
        MainWindow.SCREEN_DASHBOARD = self.stack_widget.addWidget(DashboardScreen(self.stack_widget))

        # TODO: this does not yet check if token sig is valid and such
        if token_util.read_token():
            self.stack_widget.setCurrentIndex(MainWindow.SCREEN_DASHBOARD)

    def logout_clicked(self):
        token_util.delete_token()
        self.stack_widget.removeWidget(self.stack_widget.widget(MainWindow.SCREEN_DASHBOARD))
        MainWindow.SCREEN_DASHBOARD = self.stack_widget.addWidget(DashboardScreen(self.stack_widget))
        self.stack_widget.setCurrentIndex(MainWindow.SCREEN_LOGIN)

    def page_change(self, new_index: int):
        # TODO: might need to change this on new screen added, if having something that's not dashboard too
        if new_index == MainWindow.SCREEN_DASHBOARD:
            self.logout_action.setEnabled(True)
        else:
            self.logout_action.setEnabled(False)