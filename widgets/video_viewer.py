from PySide6.QtCore import QUrl
from PySide6.QtGui import Qt, QPixmap, QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QHBoxLayout, QSlider
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class VideoViewer(QWidget):
    def __init__(self, row=None):
        super().__init__()

        # Predefined Variables
        self.layout = QVBoxLayout(self)

        self.videoFile = row[2]
        self.videoThumbnail = row[7]
        self.videoDuration = row[8]

        self.default_volume = 10
        self.maximum_volume = 100
        self.thumbnail_timestamp = 1.0

        # Default None Variables
        self.thumbnail_label = None
        self.video_widget = None
        self.media_player = None
        self.audio_player = None
        self.thumbnail_visible = None
        self.video_playing = None

        self.action_button = None
        self.scrubber_panel = None
        self.scrubber_slider = None
        self.volume_panel = None
        self.volume_slider = None
        self.volume_slider_label = None

        # Startup Functions
        self.init_ui()
        self.init_controls()
        self.init_connections()
        self.init_finish()

    def init_ui(self):
        self.thumbnail_label = QLabel()

        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.video_widget.hide()

        self.media_player = QMediaPlayer(None)
        self.audio_player = QAudioOutput()

        self.layout.addWidget(self.thumbnail_label)
        self.layout.addWidget(self.video_widget)

        self.thumbnail_visible = True
        self.video_playing = False

    def init_controls(self):
        # Play/Pause Button
        self.action_button = QPushButton("Play")
        self.action_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Scrubber Slider
        self.scrubber_panel = QHBoxLayout()

        self.scrubber_slider = QSlider(Qt.Orientation.Horizontal)
        self.scrubber_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrubber_slider.setRange(0, 0)
        self.scrubber_slider.setValue(0)

        self.scrubber_panel.addWidget(self.scrubber_slider)

        # Volume Slider
        self.volume_panel = QHBoxLayout()
        self.volume_slider_label = QLabel("Volume")

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.volume_slider.setRange(0, self.maximum_volume)
        self.volume_slider.setValue(self.default_volume)

        self.volume_panel.addWidget(self.volume_slider_label)
        self.volume_panel.addWidget(self.volume_slider)

        # Add Controls to Layout
        self.layout.addWidget(self.action_button)
        self.layout.addLayout(self.scrubber_panel)
        self.layout.addLayout(self.volume_panel)

    def init_connections(self):
        self.action_button.clicked.connect(self.toggle_video)
        self.scrubber_slider.sliderMoved.connect(self.seek_video)

        action_button_shortcut = QShortcut(QKeySequence("Space"), self)
        action_button_shortcut.activated.connect(self.toggle_video)

        self.volume_slider.valueChanged.connect(lambda: self.audio_player.setVolume(
            self.volume_slider.value() / float(self.maximum_volume)
        ))

        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.positionChanged.connect(self.update_position)

    def init_finish(self):
        self.media_player.setSource(QUrl.fromLocalFile(self.videoFile))
        self.scrubber_slider.setRange(0, float(self.videoDuration).__floor__())

        # Make Thumbnail on the fly
        self.get_thumbnail()

    def toggle_video(self):
        if self.video_playing:
            self.media_player.pause()
            self.action_button.setText("Play")

        else:
            self.media_player.setVideoOutput(self.video_widget)
            self.media_player.setAudioOutput(self.audio_player)
            self.audio_player.setVolume(self.default_volume / self.maximum_volume)

            if self.thumbnail_visible:
                self.thumbnail_label.hide()
                self.video_widget.show()
                self.thumbnail_visible = False

            self.media_player.play()
            self.action_button.setText("Pause")

        self.video_playing = not self.video_playing

    def get_thumbnail(self):
        thumbnail_map = QPixmap(self.videoThumbnail)

        scaled_thumbnail_map = thumbnail_map.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.thumbnail_label.setPixmap(scaled_thumbnail_map)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.show()

    def stop_video(self):
        if self.video_playing:
            self.media_player.stop()
            self.layout.removeWidget(self.video_widget)
            self.video_playing = False
            self.action_button.setText("Play")

    def seek_video(self, position):
        if self.media_player:
            self.media_player.setPosition(position)

    def update_duration(self, duration):
        self.scrubber_slider.setRange(0, duration)

    def update_position(self, position):
        if hasattr(self, "scrubber_slider") and self.scrubber_slider:
            self.scrubber_slider.setValue(position)
