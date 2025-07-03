import sqlite3


class Database:
    def __init__(self, db_name="media.db"):
        self.db_name = db_name
        self.db_table_name = "media_files"
        self.db_table_param_tags = [
            "ID", "Title", "File Path", "Media Type",
            "File URL", "Tags", "Date Added",
            "Thumbnail Path", "Duration"
        ]

        self._create_table()
        self._update_db_schema()

    def _create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.db_table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    file_path TEXT NOT NULL UNIQUE,
                    media_type TEXT NOT NULL,
                    file_url TEXT,
                    tags TEXT,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def _update_db_schema(self):
        new_columns = {

        }

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.db_table_name});")
            existing_columns = [row[1] for row in cursor.fetchall()]

            for col in self.db_table_param_tags:
                formatted_col = col.lower().replace(" ", "_")
                if formatted_col not in existing_columns:
                    col_type = new_columns.get(formatted_col, "TEXT")
                    cursor.execute(
                        f"ALTER TABLE {self.db_table_name} ADD COLUMN {formatted_col} {col_type}"
                    )

            conn.commit()

    def execute_query(self, query, params=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def fetch_all(self, query, params=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
