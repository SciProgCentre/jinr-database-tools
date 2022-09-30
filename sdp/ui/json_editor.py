from PySide2.QtWidgets import QWidget

from sdp.description import Description


class DescriptionEditor(QWidget):
    def __init__(self, description: Description):
        super(DescriptionEditor, self).__init__()


class ObjectEditor(QWidget):
    pass