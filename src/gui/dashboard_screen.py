from dataclasses import dataclass
from PyQt6.QtWidgets import *
from src.gui.dashboard.overview_screen import OverviewScreen
from src.gui.dashboard.upload_screen import UploadScreen


@dataclass
class DashboardScreen(QTabWidget):
    owner: QStackedWidget
    TAB_OVERVIEW = 0
    TAB_UPLOAD = 1

    def __init__(self, owner: QStackedWidget):
        QTabWidget.__init__(self)
        self.owner = owner

        DashboardScreen.TAB_OVERVIEW = self.addTab(OverviewScreen(self), 'Overview')
        DashboardScreen.TAB_UPLOAD = self.addTab(UploadScreen(self), 'Upload')

        self.tabBarClicked.connect(self.handle_tabbar_clicked)

    def handle_tabbar_clicked(self, index):
        if index == DashboardScreen.TAB_OVERVIEW:
            overview: OverviewScreen = self.widget(index)

            overview.refresh()