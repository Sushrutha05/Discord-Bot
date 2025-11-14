import sqlite3

def get_connection():
    return sqlite3.connect('bot_database.db')

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS LEETCODE_USER(
                        discord_id INTEGER PRIMARY KEY,
                        leetcode_username TEXT NOT NULL,
                        solved_problem INTEGER
                )
                
                """)

    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS GITHUB_REPO(
                        channel_id INTEGER NOT NULL,
                        repo_name TEXT NOT NULL,
                        last_commit_sha TEXT,
                        PRIMARY KEY (channel_id, repo_name)
                )
                
                """)
    conn.commit()
    conn.close()