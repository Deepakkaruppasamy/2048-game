import sqlite3
import bcrypt

DB_NAME = 'high_scores.db'

def get_connection():
    """Create and return a new SQLite connection to the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def create_table():
    """Initialize the database with the necessary table."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                username TEXT PRIMARY KEY,
                                password TEXT,
                                high_score INTEGER DEFAULT 0
                              )''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
        finally:
            conn.close()

def signup(username, password):
    """Sign up a new user with a hashed password."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            cursor.execute("INSERT INTO users (username, password, high_score) VALUES (?, ?, ?)", 
                           (username, hashed_password, 0))
            conn.commit()
            return True, "Signup successful!"
        except sqlite3.IntegrityError:
            return False, "Username already exists. Please choose a different username."
        finally:
            conn.close()
    else:
        return False, "Database connection error."

def login(username, password):
    """Log in an existing user by checking their password."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result and bcrypt.checkpw(password.encode(), result[0]):
            return True, "Login successful!"
        else:
            return False, "Invalid username or password."
    else:
        return False, "Database connection error."

def get_high_score(username):
    """Retrieve the high score for the specified user."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT high_score FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    else:
        print("Database connection error.")
        return 0

def save_high_score(username, score):
    """Update the high score for the user if the new score is higher."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET high_score = ? WHERE username = ? AND high_score < ?", 
                       (score, username, score))
        conn.commit()
        conn.close()
    else:
        print("Database connection error.")
