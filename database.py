import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            pw TEXT,
            login_time TEXT
        )
    ''')

    c.execute(
        "INSERT OR IGNORE INTO users (id, pw, login_time) VALUES (?, ?, ?)",
        ('admin', 'admin123', '')
    )

    conn.commit()
    conn.close()


def save_to_sql(df):
    conn = sqlite3.connect('users.db')

    # Fix column names
    df.columns = [str(col).strip().replace(" ", "_") for col in df.columns]

    df.to_sql('data_table', conn, if_exists='replace', index=False)

    conn.close()
