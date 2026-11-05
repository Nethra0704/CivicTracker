import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'roadintel.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Citizen', 'Authority', 'Admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_path TEXT,
            description TEXT NOT NULL,
            location_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('Low', 'Medium', 'High')),
            status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'In Progress', 'Completed')),
            severity_score INTEGER DEFAULT 50,
            confidence_score REAL DEFAULT 90.0,
            category TEXT DEFAULT 'Pothole',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # 3. comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # 4. authority_updates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authority_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            authority_id INTEGER NOT NULL,
            previous_status TEXT NOT NULL,
            new_status TEXT NOT NULL,
            response_notes TEXT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE,
            FOREIGN KEY (authority_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # 5. route_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS route_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_location TEXT NOT NULL,
            destination TEXT NOT NULL,
            safety_level TEXT NOT NULL CHECK(safety_level IN ('Safe', 'Moderate Risk', 'High Risk')),
            travel_time TEXT NOT NULL,
            toll_count INTEGER DEFAULT 0,
            traffic_level TEXT NOT NULL,
            distance TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# User helpers
def create_user(username, password, role='Citizen'):
    conn = get_db_connection()
    try:
        hashed_pw = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            (username.strip(), hashed_pw, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE LOWER(username) = LOWER(?)', (username.strip(),)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def verify_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password'], password):
        return user
    return None

# Report helpers
def create_report(user_id, image_path, description, location_name, latitude, longitude,
                  priority='Medium', status='Pending', severity_score=50, confidence_score=90.0, category='Pothole'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reports (user_id, image_path, description, location_name, latitude, longitude,
                             priority, status, severity_score, confidence_score, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, image_path, description, location_name, latitude, longitude,
          priority, status, severity_score, confidence_score, category))
    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id

def get_all_reports(priority=None, status=None, search=None, limit=100):
    conn = get_db_connection()
    query = '''
        SELECT r.*, u.username as reporter_name, u.role as reporter_role,
               (SELECT COUNT(*) FROM comments c WHERE c.report_id = r.id) as comment_count
        FROM reports r
        JOIN users u ON r.user_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if priority and priority != 'All':
        query += ' AND r.priority = ?'
        params.append(priority)
        
    if status and status != 'All':
        query += ' AND r.status = ?'
        params.append(status)
        
    if search:
        query += ' AND (r.location_name LIKE ? OR r.description LIKE ? OR r.category LIKE ?)'
        like_str = f'%{search}%'
        params.extend([like_str, like_str, like_str])
        
    query += ' ORDER BY r.created_at DESC LIMIT ?'
    params.append(limit)
    
    reports = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in reports]

def get_report_by_id(report_id):
    conn = get_db_connection()
    query = '''
        SELECT r.*, u.username as reporter_name, u.role as reporter_role,
               (SELECT COUNT(*) FROM comments c WHERE c.report_id = r.id) as comment_count
        FROM reports r
        JOIN users u ON r.user_id = u.id
        WHERE r.id = ?
    '''
    report = conn.execute(query, (report_id,)).fetchone()
    conn.close()
    return dict(report) if report else None

def get_reports_by_user(user_id):
    conn = get_db_connection()
    query = '''
        SELECT r.*, 
               (SELECT COUNT(*) FROM comments c WHERE c.report_id = r.id) as comment_count
        FROM reports r
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    '''
    reports = conn.execute(query, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in reports]

def update_report_status(report_id, new_status, authority_id=None, response_notes=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # get current status
    curr = cursor.execute('SELECT status FROM reports WHERE id = ?', (report_id,)).fetchone()
    if not curr:
        conn.close()
        return False
        
    prev_status = curr['status']
    cursor.execute('UPDATE reports SET status = ? WHERE id = ?', (new_status, report_id))
    
    # log authority update if authority provided
    if authority_id:
        cursor.execute('''
            INSERT INTO authority_updates (report_id, authority_id, previous_status, new_status, response_notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (report_id, authority_id, prev_status, new_status, response_notes))
        
    conn.commit()
    conn.close()
    return True

def get_report_stats():
    conn = get_db_connection()
    total = conn.execute('SELECT COUNT(*) as count FROM reports').fetchone()['count']
    pending = conn.execute("SELECT COUNT(*) as count FROM reports WHERE status = 'Pending'").fetchone()['count']
    in_progress = conn.execute("SELECT COUNT(*) as count FROM reports WHERE status = 'In Progress'").fetchone()['count']
    completed = conn.execute("SELECT COUNT(*) as count FROM reports WHERE status = 'Completed'").fetchone()['count']
    high_priority = conn.execute("SELECT COUNT(*) as count FROM reports WHERE priority = 'High'").fetchone()['count']
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_comments = conn.execute('SELECT COUNT(*) as count FROM comments').fetchone()['count']
    conn.close()
    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'high_priority': high_priority,
        'total_users': total_users,
        'total_comments': total_comments
    }

# Comment helpers
def add_comment(report_id, user_id, comment_text):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO comments (report_id, user_id, comment)
        VALUES (?, ?, ?)
    ''', (report_id, user_id, comment_text.strip()))
    conn.commit()
    comment_id = cursor.lastrowid
    conn.close()
    return comment_id

def get_comments_by_report(report_id):
    conn = get_db_connection()
    query = '''
        SELECT c.*, u.username, u.role
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.report_id = ?
        ORDER BY c.created_at ASC
    '''
    comments = conn.execute(query, (report_id,)).fetchall()
    conn.close()
    return [dict(c) for c in comments]

# Authority update history
def get_authority_updates(report_id):
    conn = get_db_connection()
    query = '''
        SELECT au.*, u.username as authority_name
        FROM authority_updates au
        JOIN users u ON au.authority_id = u.id
        WHERE au.report_id = ?
        ORDER BY au.update_time DESC
    '''
    updates = conn.execute(query, (report_id,)).fetchall()
    conn.close()
    return [dict(u) for u in updates]

# Route History helpers
def save_route_history(user_id, start_location, destination, safety_level, travel_time, toll_count, traffic_level, distance):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO route_history (user_id, start_location, destination, safety_level, travel_time, toll_count, traffic_level, distance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, start_location, destination, safety_level, travel_time, toll_count, traffic_level, distance))
    conn.commit()
    route_id = cursor.lastrowid
    conn.close()
    return route_id

def get_user_route_history(user_id=None, limit=10):
    conn = get_db_connection()
    if user_id:
        query = 'SELECT * FROM route_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?'
        routes = conn.execute(query, (user_id, limit)).fetchall()
    else:
        query = 'SELECT * FROM route_history ORDER BY created_at DESC LIMIT ?'
        routes = conn.execute(query, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in routes]
