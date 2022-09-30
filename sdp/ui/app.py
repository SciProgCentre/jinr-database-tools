import os

from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QPushButton, QWidget, QSizePolicy

from .backend import Backend
from .central_widget import CentralWidget
from .error_log_dock import ErrorLogDock
from .settings import Settings, ConnectionDock
from .utils import ORGANIZATION_NAME, ORGANIZATION_DOMAIN, APPLICATION_NAME, get_icon, CSS_PATH


class ConnectionAction(QPushButton):

    connected = "CONNECTED\n TO DATABASE"
    disconnected = "NO CONNECTION\n TO DATABASE"

    def __init__(self, parent):
        super(ConnectionAction, self).__init__(ConnectionAction.disconnected, parent)
        self.setToolTip(self.tr("Click to open database settings"))

    def change_status(self, state):
        if state:
            self.setText(ConnectionAction.connected)
            self.setProperty("class", "success")
            self.style().unpolish(self)
            self.style().polish(self)
        else:
            self.setText(ConnectionAction.disconnected)
            self.setProperty("class", "danger")
            self.style().unpolish(self)
            self.style().polish(self)


class DatabaseWindow(QMainWindow):
    def __init__(self, backend: Backend):
        super().__init__()
        self.setWindowTitle("Database tools")
        self.setWindowIcon(get_icon("is-database-upload.svg"))
        self.backend = backend
        self.resize(backend.app_settings.window_size)
        self.init_UI()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.backend.app_settings.window_size = self.size()
        self.backend.settings.save_settings()
        self.centralWidget().closeEvent(event)
        super(DatabaseWindow, self).closeEvent(event)

    def init_UI(self):

        toolbar : QToolBar  = self.addToolBar("Toolbar")
        toolbar.setAllowedAreas(QtCore.Qt.LeftToolBarArea)
        toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        connection_dock = ConnectionDock(self, self.backend)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, connection_dock)
        connection_dock.setVisible(self.backend.app_settings.database_settings_visible)

        action = ConnectionAction(self)
        action.setProperty("class", "disconnected")
        toolbar.addWidget(action)

        def hide():
            connection_dock.setVisible(not connection_dock.isVisible())
            self.backend.app_settings.database_settings_visible = connection_dock.isVisible()

        action.clicked.connect(hide)
        self.backend.connection_status.connect(action.change_status)
        self.backend.check_connection_status()

        # Empty widget for stretch empty space
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        action = QAction("JSON\n format description", self)
        action.triggered.connect(self.backend.open_help_github)
        toolbar.addAction(action)

        error_log_dock = ErrorLogDock(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, error_log_dock)
        toolbar.addAction(error_log_dock.toggleViewAction())

        central = CentralWidget(self.backend)
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

