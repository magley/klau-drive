from PyQt6.QtWidgets import *
from src.gui.dashboard.overview_screen import OverviewScreen
from src.gui.dashboard.upload_screen import UploadScreen

class DashboardScreen(QTabWidget):
    TAB_OVERVIEW = 0
    TAB_UPLOAD = 1

    def __init__(self, win: QStackedWidget):
        QTabWidget.__init__(self)
        self.win = win

        DashboardScreen.TAB_OVERVIEW = self.addTab(OverviewScreen(self), 'Overview')
        DashboardScreen.TAB_UPLOAD = self.addTab(UploadScreen(self), 'Upload')