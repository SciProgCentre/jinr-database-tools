import os

from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QPushButton

from .backend import Backend
from .central_widget import CentralWidget
from .settings import Settings, ConnectionDock
from .utils import ORGANIZATION_NAME, ORGANIZATION_DOMAIN, APPLICATION_NAME, get_icon, FONTS_PATH, CSS_PATH


class ConnectionAction(QPushButton):

    def __init__(self, parent):
        super(ConnectionAction, self).__init__("Find connection\n to jinrdatabaseloader", parent)
        self.setToolTip("Click to open jinrdatabaseloader settings")

    def change_status(self, state):
        if state:
            self.setText("Connected\n to jinrdatabaseloader")
            self.setProperty("class", "success")
            self.style().unpolish(self)
            self.style().polish(self)
        else:
            self.setText("Find connection\n to jinrdatabaseloader")
            self.setProperty("class", "danger")
            self.style().unpolish(self)
            self.style().polish(self)


class DatabaseWindow(QMainWindow):
    def __init__(self, backend: Backend):
        super().__init__()
        self.setWindowTitle("Database tools")
        self.setWindowIcon(get_icon("is-jinrdatabaseloader-upload.svg"))
        self.backend = backend
        self.resize(backend.settings.app_settings.window_size)
        self.init_UI()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.backend.settings.app_settings.window_size = self.size()
        self.backend.settings.update_application_settings()
        self.centralWidget().closeEvent(event)
        super(DatabaseWindow, self).closeEvent(event)

    def init_UI(self):

        toolbar : QToolBar  = self.addToolBar("Toolbar")
        toolbar.setAllowedAreas(QtCore.Qt.LeftToolBarArea)
        toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        connection_dock = ConnectionDock(self, self.backend.settings)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, connection_dock)
        connection_dock.setVisible(self.backend.settings.app_settings.database_settings_visible)

        action = ConnectionAction(self)
        action.setProperty("class", "disconnected")
        toolbar.addWidget(action)

        def hide():
            connection_dock.setVisible(not connection_dock.isVisible())
            self.backend.settings.app_settings.database_settings_visible = connection_dock.isVisible()

        action.clicked.connect(hide)
        self.backend.connection_status.connect(action.change_status)
        self.backend.check_connection_status()

        action = QAction("Open json\n scheme help", self)
        action.triggered.connect(self.backend.open_help_html)
        toolbar.addAction(action)

        central = CentralWidget(self, self.backend)
        self.setCentralWidget(central)


class DatabaseApp(QApplication):

    def __init__(self, argv):
        super(DatabaseApp, self).__init__(argv)
        self.setOrganizationName(ORGANIZATION_NAME)
        self.setOrganizationDomain(ORGANIZATION_DOMAIN)
        self.setApplicationName(APPLICATION_NAME)
        settings = Settings()
        self.backend = Backend(settings)

    def apply_material(self):
        from qt_material import apply_stylesheet
        from string import Template
        apply_stylesheet(self, 'light_blue.xml', invert_secondary=True)
        stylesheet = self.styleSheet()
        with CSS_PATH.open() as fin:
            custom_stylesheet = Template(fin.read())
            new_stylesheet = stylesheet + custom_stylesheet.substitute(**os.environ)
            self.setStyleSheet(new_stylesheet)

    def start_main_window(self):
        self.window = DatabaseWindow(self.backend)
        self.apply_material()
        self.window.show()
