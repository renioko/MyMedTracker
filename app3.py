import mysql.connector
import os
from dotenv import load_dotenv



def load_server_login() -> tuple[str, str, str]:
    """loads server login"""
    load_dotenv()
    try:
        host = os.getenv('host')
        user = os.getenv('user')
        password = os.getenv('password')
    except KeyError:
        print('problem with HOST, MYSQL_USER or MYSQL_PASSWORD')
    return host, user, password

def init_database() -> tuple[ mysql.connector.MySQLConnection, mysql.connector.cursor.MySQLCursor]:
    """Initialize the database"""
    host, user, password = load_server_login()

    my_db = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        # database="MyMedTracker\\MyMedTracker-mysql"
    )

    if my_db.is_connected():
        print("Connected to MySQL Server")
    else:
        print("Connection failed")

    cursor = my_db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS MyApp_MYSQL;")
    cursor.execute("USE MyApp_MYSQL;")
    print("Database is active")
    return my_db, cursor

def create_table() -> None:
    """Create a table"""
    my_db, cursor = init_database()
    cursor.execute("CREATE TABLE IF NOT EXISTS MyMedTracker (" \
    "id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, " \
    "name VARCHAR(255) NOT NULL, " \
    "dosage VARCHAR(25) NOT NULL, " \
    "quantity INT, " \
    "date DATE, " \
    "description TEXT);")

    my_db.commit()

    print("Table created.")
    cursor.close()
    my_db.close()

if __name__ == "__main__":
    my_db, cursor = init_database()
    create_table(my_db, cursor)