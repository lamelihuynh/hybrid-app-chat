# /Users/huynhnhatlinh0305/Downloads/CO3094-weaprous/db/database.py 

import sqlite3
import datetime

DATABASE_FILE = 'hybrid_chat.db'

def get_db_connection():
    """Tạo kết nối đến database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # Giúp truy cập cột bằng tên
    return conn

def init_db():
    """Khởi tạo bảng trong database nếu chưa tồn tại."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tạo bảng để lưu thông tin các peer
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS peers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            port INTEGER NOT NULL,
            last_seen TIMESTAMP NOT NULL,
            UNIQUE(ip_address, port) -- Đảm bảo không có peer trùng lặp
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[Database] Database initialized successfully.")

def register_or_update_peer(ip, port):
    """Đăng ký một peer mới hoặc cập nhật thời gian 'last_seen' nếu đã tồn tại."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.datetime.utcnow()
    
    # INSERT OR REPLACE là một cú pháp tiện lợi của SQLite
    # Nếu peer (ip, port) đã tồn tại, nó sẽ UPDATE, nếu chưa có, nó sẽ INSERT
    cursor.execute('''
        INSERT INTO peers (ip_address, port, last_seen) VALUES (?, ?, ?)
        ON CONFLICT(ip_address, port) DO UPDATE SET last_seen=excluded.last_seen;
    ''', (ip, port, now))
    
    conn.commit()
    conn.close()

def get_active_peers(max_age_seconds=120):
    """Lấy danh sách các peer đang hoạt động (heartbeat trong khoảng thời gian gần đây)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tính toán thời điểm giới hạn
    time_threshold = datetime.datetime.utcnow() - datetime.timedelta(seconds=max_age_seconds)
    
    cursor.execute('SELECT ip_address, port FROM peers WHERE last_seen > ?', (time_threshold,))
    
    # Chuyển đổi kết quả thành danh sách các tuple (ip, port)
    peers = [(row['ip_address'], row['port']) for row in cursor.fetchall()]
    
    conn.close()
    return peers

def prune_inactive_peers(max_age_seconds=120):
    """(Tùy chọn) Xóa các peer không hoạt động khỏi database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    time_threshold = datetime.datetime.utcnow() - datetime.timedelta(seconds=max_age_seconds)
    
    cursor.execute('DELETE FROM peers WHERE last_seen <= ?', (time_threshold,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    if deleted_count > 0:
        print(f"[Database] Pruned {deleted_count} inactive peers.")

