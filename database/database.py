import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("database")

class DatabaseManager:
    def __init__(self, db_path="data/database/surveillance.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS threat_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                threat_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                object_id INTEGER,
                object_class TEXT,
                zone TEXT,
                confidence REAL,
                screenshot_path TEXT,
                description TEXT
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracking_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                track_id INTEGER NOT NULL,
                object_class TEXT NOT NULL,
                x_center REAL NOT NULL,
                y_center REAL NOT NULL,
                zone TEXT
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                coordinates TEXT NOT NULL,
                description TEXT
            );
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL
            );
            """)
            conn.commit()
            logger.info("Database initialized successfully.")

    def log_threat(self, threat_type, severity, object_id, object_class, zone, confidence, screenshot_path, description):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """
        INSERT INTO threat_events 
        (timestamp, threat_type, severity, object_id, object_class, zone, confidence, screenshot_path, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            conn.cursor().execute(query, (
                timestamp, threat_type, severity, object_id, object_class,
                zone, float(confidence), screenshot_path, description
            ))
            conn.commit()

    def get_threats(self, limit=100):
        query = "SELECT * FROM threat_events ORDER BY id DESC LIMIT ?"
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(limit,))

    def get_analytics_summary(self):
        with self.get_connection() as conn:
            total_threats = pd.read_sql_query("SELECT COUNT(*) as cnt FROM threat_events", conn).iloc[0]['cnt']
            severity_counts = pd.read_sql_query("SELECT severity, COUNT(*) as count FROM threat_events GROUP BY severity", conn)
            type_counts = pd.read_sql_query("SELECT threat_type, COUNT(*) as count FROM threat_events GROUP BY threat_type", conn)
            recent_threats = pd.read_sql_query("SELECT * FROM threat_events ORDER BY id DESC LIMIT 10", conn)
            
        return {
            "total_threats": total_threats,
            "severity_counts": severity_counts,
            "type_counts": type_counts,
            "recent_threats": recent_threats
        }
    
    def save_zone(self, name, coordinates_str, description=""):
        query = "INSERT OR REPLACE INTO zones (name, coordinates, description) VALUES (?, ?, ?)"
        with self.get_connection() as conn:
            conn.cursor().execute(query, (name, coordinates_str, description))
            conn.commit()

    def get_zones(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM zones", conn)