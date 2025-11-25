"""
SQLite Database Module for Temporary Local Logging
This stores data locally until SQL Server permissions are ready
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Database file location
DB_FILE = "defect_logs.db"


class SQLiteConnection:
    """SQLite database connection for local logging"""
    
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Create the table if it doesn't exist"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS PA_InternalScrap (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TEST_ID INTEGER,
            Entry_Date TEXT,
            Batch_Number TEXT,
            Date_Code TEXT,
            Product TEXT,
            Scrap TEXT,
            Quantity INTEGER,
            Signature TEXT,
            Notes TEXT,
            Casting_Clock INTEGER,
            Pinhole_Level INTEGER,
            Exact_Time TEXT,
            Casting_Cavity_Number TEXT,
            Core_Cavity_Number TEXT,
            Core_Clock TEXT,
            Shift_Class INTEGER,
            Location TEXT,
            Created_At TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Create and return a database connection"""
        return sqlite3.connect(self.db_file)
    
    def test_connection(self):
        """Test the database connection"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True, f"SQLite connection successful! Database: {self.db_file}"
        except Exception as e:
            return False, str(e)


def log_defect_to_database(click_data, session_info):
    """
    Log a defect entry to the SQLite database
    
    Args:
        click_data (dict): Data from the circle diagram click
        session_info (dict): Session information from Streamlit
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        db = SQLiteConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Prepare the SQL insert statement
        sql = """
        INSERT INTO PA_InternalScrap
        (
            Entry_Date,
            Batch_Number,
            Date_Code,
            Product,
            Scrap,
            Quantity,
            Signature,
            Notes,
            Casting_Clock,
            Pinhole_Level,
            Exact_Time,
            Casting_Cavity_Number,
            Core_Cavity_Number,
            Core_Clock,
            Shift_Class,
            Location
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Prepare values from click_data and session_info
        values = (
            session_info.get('date'),                    # Entry_Date
            session_info.get('batch_number'),            # Batch_Number
            session_info.get('date_code'),               # Date_Code
            session_info.get('part_number'),             # Product
            click_data.get('defect'),                    # Scrap
            1,                                           # Quantity (always 1)
            'LS',                                        # Signature (always 'LS')
            session_info.get('notes'),                   # Notes
            click_data.get('segment'),                   # Casting_Clock
            click_data.get('distance'),                  # Pinhole_Level
            click_data.get('timestamp'),                 # Exact_Time
            click_data.get('cavity'),                    # Casting_Cavity_Number
            click_data.get('cavity'),                    # Core_Cavity_Number (same as above)
            click_data.get('ring'),                      # Core_Clock
            click_data.get('angle'),                     # Shift_Class
            click_data.get('option')                     # Location
        )
        
        # Execute the insert
        cursor.execute(sql, values)
        conn.commit()
        
        # Get the inserted ID
        inserted_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return True, f"Defect logged successfully! ID: {inserted_id} (Local DB)"
        
    except Exception as e:
        return False, f"Failed to log defect: {str(e)}"


def get_all_defects():
    """Get all logged defects from the database"""
    try:
        db = SQLiteConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM PA_InternalScrap ORDER BY ID DESC")
        rows = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        cursor.close()
        conn.close()
        
        return rows, columns
        
    except Exception as e:
        return [], []


def get_defect_count():
    """Get total count of logged defects"""
    try:
        db = SQLiteConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM PA_InternalScrap")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return count
        
    except Exception as e:
        return 0


def export_to_sql_server_format():
    """
    Export all data in format ready for SQL Server import
    Returns SQL INSERT statements
    """
    try:
        db = SQLiteConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                Entry_Date, Batch_Number, Date_Code, Product, Scrap,
                Quantity, Signature, Notes, Casting_Clock, Pinhole_Level,
                Exact_Time, Casting_Cavity_Number, Core_Cavity_Number,
                Core_Clock, Shift_Class, Location
            FROM PA_InternalScrap
            ORDER BY ID
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Generate SQL INSERT statements
        sql_statements = []
        for row in rows:
            values = ', '.join([f"'{str(v)}'" if v is not None else 'NULL' for v in row])
            sql = f"""INSERT INTO [ict_spotfire_dev].[dbo].[PA_InternalScrap]
            (Entry_Date, Batch_Number, Date_Code, Product, Scrap, Quantity, Signature, Notes,
             Casting_Clock, Pinhole_Level, Exact_Time, Casting_Cavity_Number, Core_Cavity_Number,
             Core_Clock, Shift_Class, Location)
            VALUES ({values});"""
            sql_statements.append(sql)
        
        return '\n\n'.join(sql_statements)
        
    except Exception as e:
        return f"-- Error generating export: {str(e)}"


# Alias for backwards compatibility
DatabaseConnection = SQLiteConnection


if __name__ == "__main__":
    # Test the connection
    print("=" * 50)
    print("SQLite Database Test")
    print("=" * 50)
    
    db = SQLiteConnection()
    success, message = db.test_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ SUCCESS: " + message)
        print(f"\nDatabase location: {os.path.abspath(DB_FILE)}")
        print(f"Total records: {get_defect_count()}")
    else:
        print("✗ FAILED: " + message)
    print("=" * 50)