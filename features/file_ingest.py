from moviepy import VideoFileClip
import os


class FileIngest:
    def __init__(self):
        self.thumbnail_dir = "thumbnails"

        self._create_thumbnail_dir()

    def ingestFile(self, filepath):
        # (title, file_path, media_type, file_url, tags, thumbnail_path, duration)
        split_file = filepath.split("\\")

        title = self.get_title(split_file)
        media_type = self.get_mediaType(split_file)
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

            thumbnail_name = str(os.path.basename(filepath).replace("mp4", "png"))
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
            os.mkdir(self.thumbnail_dir)

    @staticmethod
    def get_title(splitfile):
        return splitfile[-1].split(".")[0]

    @staticmethod
    def get_mediaType(splitfile):
        extension = splitfile[-1].split(".")[1]
        if extension in ["mp4"]: # Video Formats
            return "Video"
        elif extension in ["gif"]: # Animated Formats
            return "Animated"
        elif extension in ["jpg", "png", "jpeg"]: # Image Formats
            return "Image"
        else:
            return "None"