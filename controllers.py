from database import Database
from features.file_ingest import FileIngest
from pathlib import Path


import os
import random


# Pseudo-code for media ingestion from directory

    # For each file in the given directory:
    #    If file is not a .webp:
    #        Ingest file into media database
    #        Move file to sorted directory (based on extension)
    #    
    #    Else if file is a .webp:
    #        Convert webp to source file (.png or .gif)
    #        Compute hash of source file
    #
    #        If media database contains file with same hash:
    #            Update database entry to include .webp as File URL
    #            Ingest .webp into separate webp table
    #        Else:
    #            Create new media entry for source file with .webp as File URL
    #            Move source file to sorted directory
    #            Ingest .webp into separate webp table
    #
    #        Move .webp file to sorted directory

class FileIngestController:
    def __init__(self, db_controller):
        self.file_ingest = FileIngest()
        self.db_controller = db_controller

    @staticmethod
    def shortenFilePath(path):
        return os.path.basename(path)
    
    @staticmethod
    def shortenFileHash(hash):
        return hash[-10:]
    
    def ingestDirectory(self, input_dir, remove_dir=False):
        found_files = self.iterateThroughDirectory(input_dir)

        if remove_dir:
            exempt_dirs = ["duplicates", "thumbnails", "deleted"]

            for file in found_files:
                is_exempt = False

                for dir in exempt_dirs:
                    if dir in os.path.dirname(file):
                        is_exempt = True
                        continue
                
                if is_exempt:
                    continue

                item = self.file_ingest.formatFile(file)
                
                self.db_controller.removeMediaFile(item)
                self.file_ingest.relocateFile(file, delete_file=True)
            return
        
        for file in found_files:
            file_extension = Path(file).suffix

            if file_extension != ".webp":
                item = self.file_ingest.formatFile(file)
                file_hash = item[7] # Get the file hash within the item tuple

                hash_check = self.db_controller.db_instance.fetch_all(f"""
                    SELECT * FROM {self.db_controller.db_instance.db_table_name}
                    WHERE file_hash = ?;
                """, (file_hash,))
                
                if len(hash_check) > 0:
                    if any(existing[7] == file_hash for existing in hash_check):
                        self.file_ingest.relocateFile(file, duplicate=True)
                        continue
                
                new_path = self.file_ingest.relocateFile(file)

                if not new_path:
                    path_check = self.db_controller.db_instance.fetch_all(f"""
                        SELECT * FROM {self.db_controller.db_instance.db_table_name}
                        WHERE file_path = ?;
                    """, (new_path,))

                    if len(path_check) > 0:
                        self.file_ingest.relocateFile(file, duplicate=True)
                        continue

                # vomit enducing tuple editing method
                old_title, old_filepath, old_media_type, old_file_url, old_tags, old_thumbnail_path, old_duration, old_file_hash = item
                old_filepath = new_path
                item = (old_title, old_filepath, old_media_type, old_file_url, old_tags, old_thumbnail_path, old_duration, old_file_hash)

                self.db_controller.insertMediaFile(item)

            else: # For WEBP files
                self.file_ingest.relocateFile(file)
            
    def iterateThroughDirectory(self, directory):
        db_items = []
        for root, _, files in os.walk(directory):
            for file in files:
                if ".ini" in file:
                    continue

                file_path = os.path.join(root, file)
                db_items.append(file_path)
                    
        return db_items


class DatabaseController:
    def __init__(self):
        self.db_instance = Database()
        self.file_index = 1
        self.file_id_array = [row[0] for row in self.db_instance.fetch_all(f"SELECT * FROM {self.db_instance.db_table_name}")]
        
        for i in range(0, len(self.file_id_array) - 1):
            if not os.path.isfile(self.getMediaFileByID(self.file_id_array[i])[2]):
                self.file_id_array.pop(i)

        self.file_index_minimum = 1
        self.file_index_maximum = self.getTableDimensions()[0]

        self.shuffleMedia()

    def getMediaFile(self):
        # Subtracting 1 from the file index to account for arrays starting at 0
        if self.file_id_array:
            file_id = self.file_id_array[self.file_index - 1]
        else:
            return

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
        try:
            self.db_instance.execute_query(f"""
                INSERT INTO {self.db_instance.db_table_name} \
                (title, file_path, media_type, file_url, tags, thumbnail_path, duration, file_hash) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, curated_row)
        except Exception as e:
            print(f"{curated_row} caused an error for reason:\n{e}\n\n")

    def removeMediaFile(self, curated_row):
        title, file_path, media_type, file_url, tags, thumbnail_path, duration, file_hash = curated_row
        
        try:
            self.db_instance.execute_query(f"""
                DELETE FROM {self.db_instance.db_table_name} \
                WHERE title = ? AND file_path = ?
            """, (title, file_path))
        except Exception as e:
            print(f"{curated_row} caused an error for reason:\n{e}\n\n")
