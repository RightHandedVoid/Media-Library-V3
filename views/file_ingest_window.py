from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from PySide6.QtGui import Qt

from controllers import FileIngestController, DatabaseController


import easygui


class FileIngestWindow(QDialog):
    def __init__(self):
        super().__init__()

        # Class-wide Variables
        self.mainLayout = None
        self.headerLayout = None
        self.bodyLayout = None

        self.manageDirectoryTextBox = None
        self.manageDirectorySubmitButton = None

        self.addFileDirectoryButton = None
        self.removeFileDirectoryButton = None

        self.ingestedFileTable = None

        # Defining Other Classes
        self.databaseController = None
        self.fileIngestController = None

        # Initialization Functions
        self._initWindow()
        self._initControllers()
        self._initLayout()
        self._initHeaderLayout()
        self._initBodyLayout()

        self._populateTable()

        self._finalizeWindow()

    def _initWindow(self):
        self.setWindowTitle("File Ingest Menu")
        self.setGeometry(100, 100, 600, 800)
        self.setModal(True)

    def _initControllers(self):
        self.databaseController = DatabaseController()
        self.fileIngestController = FileIngestController()

    def _initLayout(self):
        self.mainLayout = QVBoxLayout()
        self.headerLayout = QHBoxLayout()
        self.bodyLayout = QHBoxLayout()

        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addLayout(self.bodyLayout)

        self.setLayout(self.mainLayout)

    def _initHeaderLayout(self):
        self.addFileDirectoryButton = self._create_button("Add Directory", callback=self._addDirectory)
        self.removeFileDirectoryButton = self._create_button("Remove Directory", callback=self._removeDirectory)

        self.headerLayout.addWidget(self.addFileDirectoryButton)
        self.headerLayout.addWidget(self.removeFileDirectoryButton)

    def _initBodyLayout(self):
        self.ingestedFileTable = QTableWidget()

        self.bodyLayout.addWidget(self.ingestedFileTable)

    @staticmethod
    def _create_button(text, **kwargs):
        callback = kwargs.get("callback", None)

        button = QPushButton(text)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.clicked.connect(callback)
        return button

    def _addDirectory(self):
        directory = easygui.diropenbox(title="Select a Directory", default="*")
        created_dbItems = self.fileIngestController.iterateThroughDirectory(directory)

        for item in created_dbItems:
            self.databaseController.insertMediaFile(item)

        self._refreshTable()

    def _removeDirectory(self):
        directory = easygui.diropenbox(title="Select a Directory", default="*")
        created_dbItems = self.fileIngestController.iterateThroughDirectory(directory)

        for item in created_dbItems:
            self.databaseController.removeMediaFile(item)

        self._refreshTable()

    def _refreshTable(self):
        self.ingestedFileTable.clearContents()

        self._populateTable()

    def _populateTable(self):
        db_tableDimensions = self.databaseController.getTableDimensions()
        existing_files = self.databaseController.getAllMediaFiles()

        self.ingestedFileTable.setRowCount(db_tableDimensions[0])
        self.ingestedFileTable.setColumnCount(db_tableDimensions[1])

        self.ingestedFileTable.setHorizontalHeaderLabels(self.databaseController.db_instance.db_table_param_tags)

        for i in range(0, len(existing_files)):             # "i" is our row
            for i2 in range(0, len(existing_files[i])):     # "i2" is our column
                if i2 == 2:  # 2 is the index of the File Path
                    itemText = (
                        f".../{self.fileIngestController.shortenFilePath(str(existing_files[i][i2]))}"
                    )

                else:
                    itemText = str(existing_files[i][i2])

                tableItem = QTableWidgetItem()
                tableItem.setText(itemText)

                self.ingestedFileTable.setItem(i, i2, tableItem)

        self.ingestedFileTable.resizeColumnsToContents()

    def _finalizeWindow(self):
        self.ingestedFileTable.resizeColumnsToContents()

        table_width = self.ingestedFileTable.verticalHeader().width()
        for col in range(self.ingestedFileTable.columnCount()):
            table_width += self.ingestedFileTable.columnWidth(col)

        if self.ingestedFileTable.verticalScrollBar().isVisible():
            table_width += self.ingestedFileTable.verticalScrollBar().width()

        table_width += self.ingestedFileTable.frameWidth() * 2
        table_width += 34

        self.setFixedWidth(table_width)
