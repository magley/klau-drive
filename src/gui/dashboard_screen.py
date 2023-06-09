from dataclasses import dataclass
from PyQt6.QtWidgets import *
from PyQt6.QtGui import  QShowEvent

from src.gui.dashboard.family_screen import FamilyScreen
from src.gui.dashboard.overview_screen import OverviewScreen
from src.gui.dashboard.my_sharing import MySharingScreen


@dataclass
class DashboardScreen(QTabWidget):
    owner: QStackedWidget
    TAB_OVERVIEW = 0
    TAB_MY_SHARING = 2
    TAB_FAMILY = 3

    def __init__(self, owner: QStackedWidget):
        QTabWidget.__init__(self)
        self.owner = owner

        DashboardScreen.TAB_OVERVIEW = self.addTab(OverviewScreen(self), 'Overview')
        DashboardScreen.TAB_MY_SHARING = self.addTab(MySharingScreen(self), "My sharing")
        DashboardScreen.TAB_FAMILY = self.addTab(FamilyScreen(self), "Family verifications")

        self.tabBarClicked.connect(self.handle_tabbar_clicked)

    def showEvent(self, event: QShowEvent) -> None:
        # this might cause problems later if messing with page showing
        self.refresh_files()

    def handle_tabbar_clicked(self, index):
        if index == DashboardScreen.TAB_OVERVIEW:
            self.refresh_files()

    def refresh_files(self):
        overview: OverviewScreen = self.widget(DashboardScreen.TAB_OVERVIEW)
        overview.refresh()
