from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from PySide6.QtGui import Qt, QShortcut, QKeySequence

from controllers import DatabaseController, FileIngestController

from views.file_ingest_window import FileIngestWindow

from widgets.viewer import Viewer


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Class-wide Variables
        self.mainLayout = None
        self.headerLayout = None
        self.bodyLayout = None
        self.footerLayout = None

        self.fileIngestWindow = None

        self.fileIngestButton = None
        self.decrementMediaButton = None
        self.incrementMediaButton = None

        self.viewer = None

        # Controllers
        self.dbController = DatabaseController()
        self.fiController = FileIngestController()

        # Initialization Functions
        self._initWindow()
        self._initLayout()
        self._initOtherWindows()
        self._initHeaderLayout()
        self._initBodyLayout()
        self._initFooterLayout()
        self._initShortcuts()

    def _initWindow(self):
        self.setWindowTitle("Media Library")
        self.setGeometry(100, 100, 800, 600)

    def _initLayout(self):
        self.headerLayout = QHBoxLayout()
        self.bodyLayout = QHBoxLayout()
        self.footerLayout = QHBoxLayout()

        self.mainLayout = QVBoxLayout()

        self.mainLayout.addLayout(self.headerLayout)
        self.mainLayout.addLayout(self.bodyLayout)
        self.mainLayout.addLayout(self.footerLayout)

        self.setLayout(self.mainLayout)

    def _initOtherWindows(self):
        self.fileIngestWindow = FileIngestWindow(self.dbController, self.fiController)

    def _initHeaderLayout(self):
        self.fileIngestButton = self._create_button(
            "Ingest Files",
            callback=self._openFileIngestWindow
        )

        self.headerLayout.addWidget(self.fileIngestButton)

    def _initBodyLayout(self):
        self.viewer = Viewer(self.dbController)

        self.bodyLayout.addWidget(self.viewer)

    def _initFooterLayout(self):
        self.decrementMediaButton = self._create_button(
            "Previous",
            callback=self._decrementMedia
        )
        self.incrementMediaButton = self._create_button(
            "Next",
            callback=self._incrementMedia
        )

        self.footerLayout.addWidget(self.decrementMediaButton)
        self.footerLayout.addWidget(self.incrementMediaButton)

    def _initShortcuts(self):
        decrement_shortcut = QShortcut(QKeySequence("Left"), self)
        decrement_shortcut.activated.connect(self._decrementMedia)

        increment_shortcut = QShortcut(QKeySequence("Right"), self)
        increment_shortcut.activated.connect(self._incrementMedia)

        firstmedia_shortcut = QShortcut(QKeySequence("Down"), self)
        firstmedia_shortcut.activated.connect(self._goToFirstMedia)

        lastmedia_shortcut = QShortcut(QKeySequence("Up"), self)
        lastmedia_shortcut.activated.connect(self._goToLastMedia)

        shufflemedia_shortcut = QShortcut(QKeySequence("R"), self)
        shufflemedia_shortcut.activated.connect(self._shuffleMedia)

    @staticmethod
    def _create_button(text, **kwargs):
        callback = kwargs.get("callback", None)

        button = QPushButton(text)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.clicked.connect(callback)
        return button

    def _openFileIngestWindow(self):
        self.fileIngestWindow.open()
        self.fileIngestWindow.raise_()

    def _shuffleMedia(self):
        self.dbController.shuffleMedia()
        self.viewer.refreshMedia()

    def _goToFirstMedia(self):
        self.dbController.goToFirstFile()
        self.viewer.refreshMedia()
    
    def _goToLastMedia(self):
        self.dbController.goToLastFile()
        self.viewer.refreshMedia()

    def _decrementMedia(self):
        self.dbController.decrementFileIndex()
        self.viewer.refreshMedia()

    def _incrementMedia(self):
        self.dbController.incrementFileIndex()
        self.viewer.refreshMedia()
