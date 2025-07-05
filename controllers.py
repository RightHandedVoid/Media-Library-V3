from database import Database
from features.file_ingest import FileIngest


import os
import random


class FileIngestController:
    def __init__(self):
        self.file_ingest = FileIngest()

    @staticmethod
    def shortenFilePath(path):
        return os.path.basename(path)

    def iterateThroughDirectory(self, directory):
        db_items = []
        for root, _, files in os.walk(directory):
            for file in files:
                if ".ini" in file:
                    continue
            
                if ".webp" in file:
                    continue

                db_items.append(
                    self.file_ingest.ingestFile(os.path.join(root, file))
                )
        return db_items


class DatabaseController:
    def __init__(self):
        self.db_instance = Database()
        self.file_index = 1
        self.file_id_array = [row[0] for row in self.db_instance.fetch_all(f"SELECT * FROM {self.db_instance.db_table_name}")]

        self.file_index_minimum = 1
        self.file_index_maximum = self.getTableDimensions()[0]

        self.shuffleMedia()

    def getMediaFile(self):
        # Subtracting 1 from the file index to account for arrays starting at 0
        file_id = self.file_id_array[self.file_index - 1]

        mediaArray = self.db_instance.fetch_all(f"""
            SELECT * FROM {self.db_instance.db_table_name} WHERE id = {file_id} \
        """)

        if len(mediaArray) == 0:
            return None
        return mediaArray[0]

    def getMediaFileByID(self, Id):
        media = self.db_instance.fetch_all(f"""
            SELECT * FROM {self.db_instance.db_table_name} WHERE id = {Id} \
        """)

        if len(media) == 0:
            return None
        return media[0]
    
    def shuffleMedia(self):
        if len(self.file_id_array) > 0:
            random.shuffle(self.file_id_array)

    def goToFirstFile(self):
        if self.file_index > self.file_index_minimum:
            self.file_index = 1
    
    def goToLastFile(self):
        if self.file_index < self.file_index_maximum:
            self.file_index = self.file_index_maximum

    def incrementFileIndex(self):
        if self.file_index < self.file_index_maximum:
            self.file_index += 1

    def decrementFileIndex(self):
        if self.file_index > self.file_index_minimum:
            self.file_index -= 1

    def getTableDimensions(self):
        row_info = self.db_instance.fetch_all(f"""
            SELECT COUNT (*) FROM {self.db_instance.db_table_name}
        """)
        column_info = self.db_instance.fetch_all(f"""
            PRAGMA table_info(
                {self.db_instance.db_table_name}
            )
        """)

        table_rows = row_info[0][0]
        table_columns = len([item[1] for item in column_info])

        return (table_rows if table_rows is not None else 0,
                table_columns if table_columns is not None else 0)

    def getAllMediaFiles(self):
        return self.db_instance.fetch_all(f"""
            SELECT * FROM {self.db_instance.db_table_name}
        """)

    def insertMediaFile(self, curated_row):
        self.db_instance.execute_query(f"""
            INSERT INTO {self.db_instance.db_table_name} \
            (title, file_path, media_type, file_url, tags, thumbnail_path, duration) \
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, curated_row)

    def removeMediaFile(self, curated_row):
        title, file_path, media_type, file_url, tags, thumbnail_path, duration = curated_row
        self.db_instance.execute_query(f"""
            DELETE FROM {self.db_instance.db_table_name} \
            WHERE title = ? AND file_path = ?
        """, (title, file_path))
