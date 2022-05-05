import logging

from PySide2.QtWidgets import QDockWidget, QPlainTextEdit

class ErrorHandler(logging.Handler):
    def __init__(self, widget: QPlainTextEdit):
        super(ErrorHandler, self).__init__()
        self.widget = widget

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class ErrorLogDock(QDockWidget):
    def __init__(self, parent):
        super().__init__("Error panel", parent)
        widget = QPlainTextEdit()
        self.setWidget(widget)
        widget.setReadOnly(True)
        handler = ErrorHandler(widget)
        logging.root.addHandler(handler)