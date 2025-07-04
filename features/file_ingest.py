from moviepy import VideoFileClip
import os


class FileIngest:
    def __init__(self):
        self.thumbnail_dir = "thumbnails"

        self._create_thumbnail_dir()

    def ingestFile(self, filepath):
        """Ingest a file and return the DB ready tuple."""
        # (title, file_path, media_type, file_url, tags, thumbnail_path, duration)
        filename = os.path.basename(filepath)

        title = self.get_title(filename)
        media_type = self.get_mediaType(filename)
        file_url = None
        tags = None

        thumbnail_path = None
        duration = None

        if media_type == "Video":
            thumbnail_path, duration = self.get_video_metadata(filepath)

        return (title, filepath, media_type,
                file_url, tags, thumbnail_path, duration)

    def get_video_metadata(self, filepath):
        try:
            clip = VideoFileClip(filepath)
            duration = clip.duration

            base, _ = os.path.splitext(os.path.basename(filepath))
            thumbnail_name = f"{base}.png"
            thumbnail_path = os.path.join(
                self.thumbnail_dir,
                thumbnail_name
            )

            clip.save_frame(thumbnail_path, t=1.0)
            clip.close()
            return thumbnail_path, duration

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return None, None

    def _create_thumbnail_dir(self):
        if not os.path.isdir(self.thumbnail_dir):
            os.makedirs(self.thumbnail_dir, exist_ok=True)

    @staticmethod
    def get_title(filename: str) -> str:
        """Return the filename without its extension."""
        return os.path.splitext(filename)[0]

    @staticmethod
    def get_mediaType(filename: str) -> str:
        """Return the media type based on file extension."""
        extension = os.path.splitext(filename)[1].lstrip(".").lower()
        if extension in ["mp4"]:  # Video Formats
            return "Video"
        elif extension in ["gif"]:  # Animated Formats
            return "Animated"
        elif extension in ["jpg", "png", "jpeg"]:  # Image Formats
            return "Image"
        else:
            return "None"
