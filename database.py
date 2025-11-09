import sqlite3

def init_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            phone_number TEXT NOT NULL,
            session_string TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, phone_number, session_string):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (user_id, phone_number, session_string) VALUES (?, ?, ?)',
              (user_id, phone_number, session_string))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def remove_user(user_id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
