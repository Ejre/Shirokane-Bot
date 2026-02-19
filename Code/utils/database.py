"""
Database Utility for Leveling System
Uses SQLite to store user XP and levels.
"""

import sqlite3
import os

DB_DIR = "data"
DB_FILE = os.path.join(DB_DIR, "leveling.db")

def initialize_database():
    """Initialize the database and create tables if they don't exist."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 0
        )
    """)
    
    # Create Role Rewards Table (Optional, for future extensibility)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_rewards (
            level INTEGER PRIMARY KEY,
            role_id TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_FILE}")

def get_connection():
    """Get a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def get_user_data(user_id):
    """Get user data (xp, level) or create default if not exists."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (str(user_id),))
    data = cursor.fetchone()
    
    if not data:
        # Create new user entry
        cursor.execute("INSERT INTO users (user_id, xp, level) VALUES (?, 0, 0)", (str(user_id),))
        conn.commit()
        data = (0, 0)
        
    conn.close()
    return {"xp": data[0], "level": data[1]}

def update_user_xp(user_id, new_xp, new_level):
    """Update user's XP and Level."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (new_xp, new_level, str(user_id)))
    
    conn.commit()
    conn.close()

def get_top_users(limit=10):
    """Get top users by XP."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, xp, level FROM users ORDER BY xp DESC LIMIT ?", (limit,))
    data = cursor.fetchall()
    
    conn.close()
    return data
