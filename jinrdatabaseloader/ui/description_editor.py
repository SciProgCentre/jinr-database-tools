from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QComboBox, QGroupBox, QPushButton, QBoxLayout, \
    QScrollArea, QCheckBox, QStackedLayout, QSpinBox

from jinrdatabaseloader.description import Description
from jinrdatabaseloader.ui.backend import Backend
from jinrdatabaseloader.ui.description_model import FDItem, FDFilesTree, PathItem
from jinrdatabaseloader.ui.utils import hbox


class NameEditor(QWidget):
    def __init__(self, item):
        super(NameEditor, self).__init__()
        name_editor = QLineEdit(item.name)
        wrong_name_label = QLabel(self.tr("This name already exist"))
        wrong_name_label.setVisible(False)

        def finish():
            new_name = name_editor.text()
            if new_name != item.name:
                if FDFilesTree.check_name(item.collection, new_name):
                    item.name = new_name
                else:
                    wrong_name_label.setVisible(True)

        name_editor.editingFinished.connect(finish)
        name_editor.textChanged.connect(lambda: wrong_name_label.setVisible(False))

        layout = hbox((QLabel(self.tr("Description name: ")), 1),
                      name_editor, wrong_name_label)
        self.setLayout(layout)


class DatabaseBasedField(QWidget):
    change_value = Signal(str)

    def __init__(self, description: Description, backend: Backend, database_callback, key: str, tooltip_name: str = ""):
        super(DatabaseBasedField, self).__init__()
        self._no_connection = self.tr("Not connection to database")
        self._combo_tooltip = self.tr("Select {} from database".format(tooltip_name))
        self.backend = backend
        self.callback = database_callback
        self.combo = QComboBox()
        self.update_combo_list()
        combo = self.combo
        editor = QLineEdit(description[key])

        def update():
            text = editor.text()
            description[key] = text
            self.change_value.emit(text)

        editor.editingFinished.connect(update)

        def update_combo():
            editor.setText(combo.currentText())
            update()

        combo.currentTextChanged.connect(update_combo)

        hbox(
            editor,
            combo,
            parent=self
        )

        def update_connect(status):
            if status:
                combo.setToolTip(self._combo_tooltip)
            else:
                combo.setToolTip(self._no_connection)

        backend.connection_status.connect(update_connect)

    def update_combo_list(self):
        self.combo.clear()
        if self.backend.database.test_connect():
            self.combo.addItems(self.callback(self.backend.database))
            self.combo.setToolTip(self._combo_tooltip)
        else:
            self.combo.setToolTip(self._no_connection)


class TableChooser(QGroupBox):
    def __init__(self, description: Description, backend: Backend):
        super(TableChooser, self).__init__()
        self.setTitle(self.tr("Select target table"))
        vbox = QVBoxLayout(self)
        self.widget = DatabaseBasedField(description, backend, lambda database: database.tables_name, "table", "table")
        vbox.addWidget(self.widget)


class FormatChooser(QComboBox):
    def __init__(self, description):
        super(FormatChooser, self).__init__()
        values = description.avaiable_enum_values("format")
        self.addItems(values)
        self.currentTextChanged.connect(lambda text: description.__setitem__("format", text))


def get_description_property_editor(key, description: Description, parent) -> QBoxLayout:
    widgets = []
    type = description.property_type(key)
    widgets.append((QLabel(key.title() + ":"), 1))
    if type.is_bool:
        editor = QCheckBox()
        editor.setChecked(description[key])
        editor.clicked.connect(lambda state: description.__setitem__(key, state))
    elif type.is_int:
        editor = QSpinBox()
        editor.setValue(description[key])
        editor.valueChanged.connect(lambda x: description.__setitem__(key, x))
    else:
        editor = QLineEdit(str(description[key]))

        def set():
            value = editor.text()
            description.__setitem__(key, value)

        editor.editingFinished.connect(set)
    widgets.append((editor, 1))
    help_label = QLabel("?")
    help_label.setProperty("class", "help")
    help_label.setToolTip(description.get_docs(key))
    widgets.append(help_label)
    return hbox(*widgets, parent=parent)


class ParserSettings(QWidget):

    def __init__(self, description: Description):
        super(ParserSettings, self).__init__()
        self.description = description
        self._pages = {}
        self.init_UI()
        self.change_format(description["format"])

    def init_UI(self):
        self.stack = QStackedLayout(self)

    def change_format(self, new_format):
        settings = self.description["parser_settings"][new_format]
        indx = self._pages.get(new_format, None)
        if indx is None:
            indx = self.stack.count()
            widget = self.create_settings_editor(settings)
            self.stack.insertWidget(indx, widget)
            self._pages[new_format] = indx
        self.stack.setCurrentIndex(indx)

    def create_settings_editor(self, settings: Description):
        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        for key in settings.available_keys():
            get_description_property_editor(key, settings, vbox)
        scroll_area.setWidget(widget)
        return scroll_area


class ColumnWidget(QGroupBox):

    def __init__(self, column: Description, editor: "ColumnsEditor"):
        super(ColumnWidget, self).__init__()
        vbox = QVBoxLayout(self)
        self.column = column
        self.column_name = DatabaseBasedField(column, editor.backend,
                                              lambda database: database.table_columns(editor.description["table"]),
                                         "name", "column")

        close_button = QPushButton("X")
        close_button.setProperty("class", "danger")
        close_button.setToolTip(self.tr("Remove column"))
        close_button.clicked.connect(lambda : editor.remove_column(self))
        hbox(close_button, parent=vbox).insertStretch(0)

        hbox(
            (QLabel("Name:"), 1),
            self.column_name,
            parent=vbox
        )
        type_combo = QComboBox()
        type_combo.addItems(column.avaiable_enum_values("type"))


        hbox((QLabel("Type:"), 1),
             type_combo,
             parent=vbox
             )

    def update_table(self, table_name):
        self.column_name.update_combo_list()


class ColumnsEditor(QWidget):
    def __init__(self, description: Description, backend: Backend, table_chooser: TableChooser):
        super(ColumnsEditor, self).__init__()
        self.backend = backend
        self.description = description
        self.columns = description["columns"]
        self.table_chooser = table_chooser
        self.init_UI()

    def init_UI(self):
        vbox = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.scroll_vbox = QVBoxLayout(scroll_widget)
        self.scroll_vbox.addStretch()

        add_button = QPushButton(self.tr("+ Add column"))
        add_button.clicked.connect(self.add_column)
        for column in self.columns:
            self.create_item(column)

        scroll_area.setWidget(scroll_widget)

        vbox.addWidget(scroll_area)
        vbox.addWidget(add_button)

    def add_column(self):
        column = {"name": "column {}".format(self.scroll_vbox.count()), "type": "float"}
        column = self.columns.add_description(column)
        self.create_item(column)

    def remove_column(self, column_widget):
        self.columns.remove(column_widget.column)
        self.scroll_vbox.removeWidget(column_widget)
        column_widget.deleteLater()

    def create_item(self, column: Description):
        widget = ColumnWidget(column, self)
        self.table_chooser.widget.change_value.connect(widget.update_table)
        self.scroll_vbox.insertWidget(self.scroll_vbox.count() - 1, widget)


class DescriptionEditor(QWidget):
    _editors = {}

    def __init__(self, item: FDItem, backend: Backend):
        super(DescriptionEditor, self).__init__()
        self.item = item
        self.backend = backend
        self._update_title()
        item.sender.add_subscriber(item.NAME_ROLE, self._update_title)
        item.collection.sender.add_subscriber(item.NAME_ROLE, self._update_title)
        self.description = item.description
        self.init_UI()

    def _update_title(self):
        title = "{}/{}".format(
            self.item.collection.name,
            self.item.name,
        )
        self.setWindowTitle(title)

    def init_UI(self):
        layout = QVBoxLayout(self)

        vbox_right = QVBoxLayout()
        vbox_left = QVBoxLayout()

        vbox_left.addWidget(NameEditor(self.item))
        self.table_chooser = TableChooser(self.description, self.backend)
        vbox_left.addWidget(self.table_chooser)
        self.format_chooser = FormatChooser(self.description)
        self.parser_settings = ParserSettings(self.description)
        self.format_chooser.currentTextChanged.connect(lambda text: self.parser_settings.change_format(text))
        vbox_left.addWidget(self.format_chooser)
        vbox_left.addWidget(self.parser_settings)

        self.columns_editor = ColumnsEditor(self.description, self.backend, self.table_chooser)
        vbox_right.addWidget(self.columns_editor)

        hbox(vbox_left, vbox_right, parent=layout)
        self.init_buttons(layout)

    def init_buttons(self, vbox):
        def apply():
            self.item.setData(self.description, PathItem.DESCRIPTION_ROLE)

        def ok():
            apply()
            self.close()

        def cancel():
            self.close()

        ok_button = QPushButton(self.tr("Ok"))
        ok_button.setProperty("class", "success")
        ok_button.clicked.connect(ok)
        apply_button = QPushButton(self.tr("Apply"))
        apply_button.setProperty("class", "success")
        apply_button.clicked.connect(apply)
        cancel_button = QPushButton(self.tr("Cancel"))
        cancel_button.setProperty("class", "danger")
        cancel_button.clicked.connect(cancel)
        hbox(
            ok_button,
            apply_button,
            cancel_button,
            parent=vbox
        ).insertStretch(0)

    @staticmethod
    def open_editor(item: FDItem, backend: Backend):
        editor = DescriptionEditor._editors.get(item.path, DescriptionEditor(item, backend))
        DescriptionEditor._editors[item.path] = editor
        editor.show()
