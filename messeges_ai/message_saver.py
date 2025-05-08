import sqlite3
import datetime
import os

def get_all_messages(db_path="chat_history.db"):
    """
    Retrieves all messages from the messages table in the SQLite database.
    Returns a list of dictionaries, where each dictionary represents a message.
    """
    conn = None
    messages = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row # Access columns by name
        cursor = conn.cursor()

        # Ensure tables exist before querying (idempotent)
        _ensure_tables_exist(cursor)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages';")
        if cursor.fetchone() is None:
            # This case should ideally not be reached if _ensure_tables_exist works
            print(f"Table 'messages' does not exist in '{db_path}'.")
            return messages

        cursor.execute("""
            SELECT m.id, m.timestamp, m.user_id, m.message_text, m.conversation_id, 
                   COALESCE(u.username, 'Anonymous') as username, 
                   COALESCE(u.email, '') as email,
                   u.google_id
            FROM messages m
            LEFT JOIN users u ON m.user_id = u.id
            ORDER BY m.timestamp DESC
        """)
        rows = cursor.fetchall()

        for row in rows:
            messages.append(dict(row))
        
        return messages

    except sqlite3.Error as e:
        print(f"An error occurred while retrieving messages: {e}")
        return messages # Return empty list on error
    finally:
        if conn:
            conn.close()

def _ensure_tables_exist(cursor):
    """Helper function to ensure both users and messages tables are created."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT,
            google_id TEXT UNIQUE, -- Added for Google OAuth
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER DEFAULT 0,
            message_text TEXT NOT NULL,
            conversation_id INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

def save_message(message_content: str, user_id=0, db_path="chat_history.db"):
    """
    Saves a message to the SQLite database.
    Creates the database and table if they don't exist.
    
    Args:
        message_content: The text of the message to save.
        user_id: The ID of the user sending the message (default=0 for anonymous).
        db_path: The path to the SQLite database file.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        _ensure_tables_exist(cursor) # Ensure tables are there

        cursor.execute('''
            INSERT INTO messages (message_text, user_id)
            VALUES (?, ?)
        ''', (message_content, user_id))

        conn.commit()
        print(f"Message saved successfully to '{db_path}' for user_id: {user_id}.")

    except sqlite3.Error as e:
        print(f"An error occurred while saving message: {e}")
    finally:
        if conn:
            conn.close()

def create_user(username, email, password_hash=None, google_id=None, db_path="chat_history.db"):
    """
    Creates a new user in the database.
    
    Args:
        username: The username of the new user.
        email: The email of the new user.
        password_hash: The hashed password if using password authentication.
        google_id: The Google ID for Google OAuth.
        db_path: The path to the SQLite database file.
        
    Returns:
        The ID of the newly created user, or None if creation failed.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        _ensure_tables_exist(cursor) # Ensure tables are there
        
        # Check if user with this email or google_id already exists
        if email:
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            existing_user_by_email = cursor.fetchone()
            if existing_user_by_email:
                # Potentially update google_id if email matches but google_id is new
                if google_id:
                    cursor.execute("UPDATE users SET google_id = ? WHERE id = ? AND google_id IS NULL", (google_id, existing_user_by_email[0]))
                    conn.commit()
                return existing_user_by_email[0]
        
        if google_id:
            cursor.execute("SELECT id FROM users WHERE google_id = ?", (google_id,))
            existing_user_by_google_id = cursor.fetchone()
            if existing_user_by_google_id:
                 # Potentially update email if google_id matches but email is new/different for this entry
                if email:
                    cursor.execute("UPDATE users SET email = ? WHERE id = ? AND (email IS NULL OR email != ?)", 
                                   (email, existing_user_by_google_id[0], email))
                    conn.commit()
                return existing_user_by_google_id[0]
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, google_id)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, google_id))
        
        conn.commit()
        user_id = cursor.lastrowid
        print(f"User created/updated successfully with ID: {user_id}")
        return user_id
        
    except sqlite3.Error as e:
        print(f"An error occurred while creating/updating user: {e}")
        # Specific error for UNIQUE constraint violation if not caught above
        if "UNIQUE constraint failed: users.email" in str(e) and email:
            print(f"User with email {email} likely already exists.")
        if "UNIQUE constraint failed: users.google_id" in str(e) and google_id:
            print(f"User with google_id {google_id} likely already exists.")
        return None
    finally:
        if conn:
            conn.close()

def get_user_by_email(email, db_path="chat_history.db"):
    """
    Retrieves a user by their email address.
    
    Args:
        email: The email address to look up.
        db_path: The path to the SQLite database file.
        
    Returns:
        A dictionary with the user's details, or None if not found.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        _ensure_tables_exist(cursor) # Ensure tables are there
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            return dict(user)
        return None
        
    except sqlite3.Error as e:
        print(f"An error occurred while fetching user by email: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_by_google_id(google_id, db_path="chat_history.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        _ensure_tables_exist(cursor) # Ensure tables are there

        cursor.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
        user = cursor.fetchone()
        if user: return dict(user)
        return None
    except sqlite3.Error as e:
        print(f"An error occurred while fetching user by google_id: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Standalone testing part
def _print_messages_for_cli(messages_list):
    if not messages_list:
        print("No messages found in the table.")
        return

    print("\n--- Messages Table (CLI) ---")
    print(f"{'ID':<5} | {'Timestamp':<26} | {'User':<30} | {'Conv. ID':<10} | {'Message'}")
    print("-" * 100)

    for msg_dict in messages_list:
        message_id = msg_dict['id']
        timestamp = msg_dict['timestamp']
        user_display = f"{msg_dict['username']} (ID:{msg_dict['user_id']})"
        if msg_dict.get('google_id'): # Check if google_id exists in the dict
            user_display += f" G_ID:{msg_dict['google_id'][:10]}..." # Show partial google_id
        message_text = msg_dict['message_text']
        conversation_id = msg_dict['conversation_id']
        
        # Timestamp formatting (assuming it might be string or datetime)
        if isinstance(timestamp, str):
            try:
                dt_object = datetime.datetime.fromisoformat(timestamp.split('.')[0])
                formatted_timestamp = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                formatted_timestamp = timestamp # Fallback
        elif isinstance(timestamp, datetime.datetime):
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            formatted_timestamp = str(timestamp) # Fallback

        print(f"{message_id:<5} | {formatted_timestamp:<26} | {user_display:<30} | {conversation_id:<10} | {message_text}")
    print("--- End of Table (CLI) ---\n")

if __name__ == "__main__":
    # This part is for direct script execution for testing purposes.
    # The Flask app will use the functions directly.
    default_db_file = "chat_history.db"
    
    # Ensure the directory for the DB exists if running standalone
    os.makedirs(os.path.dirname(default_db_file), exist_ok=True)

    print(f"Running message_saver.py in standalone mode for testing with DB: {default_db_file}")

    # Test user creation (with Google ID)
    gid_test_user = "test_google_id_12345"
    email_test_user = "google_user@example.com"
    test_user_id_google = create_user("Google Test User", email_test_user, google_id=gid_test_user, db_path=default_db_file)
    if test_user_id_google:
        print(f"Created/found Google test user with ID: {test_user_id_google}")
        fetched_g_user = get_user_by_google_id(gid_test_user, db_path=default_db_file)
        # print(f"Fetched user by google_id: {fetched_g_user}")
    
    # Test regular user creation
    test_user_id_regular = create_user("Regular Test User", "regular@example.com", password_hash="hashed_pass", db_path=default_db_file)
    if test_user_id_regular:
        print(f"Created/found regular test user with ID: {test_user_id_regular}")
        # fetched_r_user = get_user_by_email("regular@example.com", db_path=default_db_file)
        # print(f"Fetched user by email: {fetched_r_user}")

    print("\nCurrent messages in the database:")
    current_messages = get_all_messages(db_path=default_db_file)
    _print_messages_for_cli(current_messages)

    try:
        user_input_message = input("Enter a message to save (or press Enter to skip): ")
        if user_input_message:
            # Save message from the Google test user if available
            user_id_to_use = test_user_id_google if test_user_id_google else 0 
            save_message(user_input_message, user_id=user_id_to_use, db_path=default_db_file)
            
            print("\nMessages after saving:")
            updated_messages = get_all_messages(db_path=default_db_file)
            _print_messages_for_cli(updated_messages)
        else:
            print("No message entered, skipping save.")
    except KeyboardInterrupt:
        print("\nStandalone test finished by user.") 