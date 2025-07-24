from moviepy import VideoFileClip
from pathlib import Path
import os
import shutil
import hashlib


class FileIngest:
    def __init__(self):
        self._master_dir = os.path.join(os.path.expanduser("~"), "Documents", "Library")
        self.thumbnail_dir = os.path.join(self._master_dir, "thumbnails")

        self._create_thumbnail_dir()

    def _create_thumbnail_dir(self):
        if not os.path.isdir(self.thumbnail_dir):
            os.makedirs(self.thumbnail_dir, exist_ok=True)

    def formatFile(self, filepath, webp=False):
        """Ingest a file and return the DB ready tuple."""
        # (title, file_path, media_type, file_url, tags, thumbnail_path, duration)
        if webp:
            return

        filename = os.path.basename(filepath)

        title = self.get_title(filename)
        media_type = self.get_mediaType(filename)
        file_url = None
        tags = None

        thumbnail_path = None
        duration = None

        file_hash = self.get_hash(filepath)

        if media_type == "Video":
            thumbnail_path, duration = self.get_video_metadata(filepath)

        return (title, filepath, media_type,
                file_url, tags, thumbnail_path, duration, file_hash)
    
    def relocateFile(self, file_path, duplicate=False, delete_file=False):
        file_extension = Path(file_path).suffix

        if duplicate:
            intended_dir = os.path.join(self._master_dir, "duplicates")
        
        elif delete_file:
            intended_dir = os.path.join(self._master_dir, "deleted")
        
        else:
            intended_dir = os.path.join(self._master_dir, file_extension)

        if not os.path.isdir(intended_dir):
            os.makedirs(intended_dir, exist_ok=True)
        
        try:
            return shutil.move(file_path, intended_dir)
        
        except Exception as e:
            return False

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
            print(f"Type of error: {type(e)}")
            return None, None
    
    @staticmethod
    def get_hash(filepath: str) -> str:
        """Return the file hash of file"""
        func = hashlib.sha256()

        with open(filepath, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                func.update(chunk)

        return func.hexdigest()

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
