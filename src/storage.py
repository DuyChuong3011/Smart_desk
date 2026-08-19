import sqlite3
import os
import csv
import logging

class EventDatabase:
    def __init__(self, db_path="logs/smart_desk.db"):
        self.db_path = db_path
        self._init_db()
        self._migrate_from_csv()

    def _init_db(self):
        """Khởi tạo bảng nếu chưa có."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                object_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                snapshot_file TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def _migrate_from_csv(self):
        """Sao chép dữ liệu cũ từ events.csv sang SQLite nếu có."""
        csv_path = os.path.join(os.path.dirname(self.db_path), "events.csv")
        
        if not os.path.exists(csv_path):
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Kiểm tra xem db đã có dữ liệu chưa. Nếu có rồi thì không migrate nữa.
        cursor.execute("SELECT COUNT(*) FROM events")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
            
        logging.info("Migrating data from events.csv to SQLite database...")
        
        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None) # Bỏ qua header
                
                if headers:
                    for row in reader:
                        if len(row) >= 3:
                            timestamp = row[0]
                            obj = row[1]
                            event = row[2]
                            snapshot = row[3] if len(row) > 3 else ""
                            
                            cursor.execute('''
                                INSERT INTO events (timestamp, object_name, event_type, snapshot_file)
                                VALUES (?, ?, ?, ?)
                            ''', (timestamp, obj, event, snapshot))
                            
            conn.commit()
            logging.info("Migration successful.")
            
            # Xoá file cũ hoặc đổi tên để tránh migrate lại
            os.rename(csv_path, csv_path + ".bak")
            
        except Exception as e:
            logging.error(f"Error migrating from CSV: {e}")
            
        finally:
            conn.close()

    def insert_event(self, timestamp, object_name, event_type, snapshot_file=""):
        """Thêm một sự kiện mới vào cơ sở dữ liệu."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (timestamp, object_name, event_type, snapshot_file)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, object_name, event_type, snapshot_file))
        
        conn.commit()
        conn.close()

    def get_recent_events(self, limit=20):
        """Lấy danh sách các sự kiện gần đây nhất (mặc định lấy 20)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sắp xếp giảm dần theo id (id lớn nhất là mới nhất)
        cursor.execute('''
            SELECT timestamp, object_name, event_type, snapshot_file
            FROM events
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append({
                "timestamp": row[0],
                "object": row[1],
                "event": row[2],
                "snapshot": row[3]
            })
            
        return events
