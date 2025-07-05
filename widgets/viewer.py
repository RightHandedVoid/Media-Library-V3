from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QStackedWidget
from PySide6.QtGui import QPixmap, Qt, QMovie
import os

from widgets.video_viewer import VideoViewer


class Viewer(QWidget):
    def __init__(self, dbController):
        super().__init__()

        # Other Classes
        self.dbController = dbController

        # Variables
        self.fileRow = None

        self.mediaLabel = None
        self.mediaMovie = None
        self.mediaVideo = None

        self.mediaPath = None
        self.mediaIndex = None

        # Startup Functions
        self._createFeatures()
        self.refreshMedia()

    def _createFeatures(self):
        self.mediaLabel = QLabel()
        self.mediaLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.mediaMovie = None

        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.stacked_widget = QStackedWidget(self)
        self.layout.addWidget(self.stacked_widget, 1, 1)

        self.mediaPath = QLabel()
        self.mediaIndex = QLabel()
        
        self.layout.addWidget(self.mediaIndex, 2, 1)
        self.layout.addWidget(self.mediaPath, 3, 1)

        self.stacked_widget.addWidget(self.mediaLabel)

    def refreshMedia(self):
        self._clearMedia()
        self.fileRow = self.dbController.getMediaFile()
        self._displayMedia()

    def _clearMedia(self):
        if self.mediaMovie:
            self.mediaMovie.stop()

        if self.mediaLabel:
            self.mediaLabel.clear()

        if self.mediaVideo:
            self.mediaVideo.stop_video()
            self.stacked_widget.removeWidget(self.mediaVideo)
            self.mediaVideo.deleteLater()
            self.mediaVideo = None
        
        if self.mediaIndex:
            self.mediaIndex.clear()

        if self.mediaPath:
            self.mediaPath.clear()

    def _displayMedia(self):
        if self.fileRow:
            fileType = self.fileRow[3]

            if fileType == "Image":
                self._displayImage()
            elif fileType == "Animated":
                self._displayMovie()
            elif fileType == "Video":
                self._displayVideo()
            
            self.updateMediaInfo()
    
    def updateMediaInfo(self):
        total_media = self.dbController.getTableDimensions()[0]
        path_parts = self.fileRow[2].split(os.sep)
        file_path = os.path.join(*path_parts[-2:])

        self.mediaIndex.setText(
            f"File Index: {self.dbController.file_index} / {total_media}"
        )
        self.mediaPath.setText(f"File Path: ..{os.sep}{file_path}")

    def _displayImage(self):
        filepath = self.fileRow[2]
        self.mediaLabel.clear()

        pixmap = QPixmap(filepath)
        scaled_pixmap = pixmap.scaled(self.mediaLabel.size(), Qt.AspectRatioMode.KeepAspectRatio)

        self.mediaLabel.setPixmap(scaled_pixmap)

    def _displayMovie(self):
        filepath = self.fileRow[2]

        self.mediaMovie = QMovie(filepath)
        original_size = self.mediaMovie.currentPixmap().size()
        scaled_size = original_size.scaled(self.mediaLabel.size(), Qt.AspectRatioMode.KeepAspectRatio)

        self.mediaMovie.setScaledSize(scaled_size)
        self.mediaLabel.setMovie(self.mediaMovie)
        self.mediaMovie.start()

    def _displayVideo(self):
        self.mediaVideo = VideoViewer(self.fileRow)

        self.stacked_widget.addWidget(self.mediaVideo)
        self.stacked_widget.setCurrentWidget(self.mediaVideo)
