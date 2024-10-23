import mysql.connector
PASSWORD = 'googleple'
DATABASE = 'products'
CREATE_TABLE = """
CREATE TABLE users (
ID INT AUTO_INCREMENT PRIMARY KEY,
Username VARCHAR(50) UNIQUE NOT NULL,
Password VARCHAR(50) NOT NULL,
Admin BOOLEAN DEFAULT FALSE
);"""


class UserDB:
    def __init__(self):
        self.database = None
        self.connect()

    def connect(self):
        """
        Connects to a SQL database
        """
        try:
            self.database = mysql.connector.connect(host='localhost', user='root', password=PASSWORD, database=DATABASE)
        except:
            raise Exception('Could not connect to database')

    def get_user(self, username: str) -> str:
        """
        Returns the password associated with the username
        Returns NONE if the user cannot be found
        """
        cursor = self.database.cursor()
        try:
            cursor.execute(f'SELECT password FROM users WHERE Username="{username}"')
        except:
            return None

        return cursor.fetchone()[0]

    def add_user(self, username: str, password: str, admin: bool = False):
        """
        Adds a user to the database
        """
        cursor = self.database.cursor()
        try:
            cursor.execute(f'INSERT INTO users (Username, Password, Admin) VALUES ("{
                           username}", "{password}", {admin})')
        except:
            print('Error adding user')
            return False
        self.database.commit()
        return True

    def create_table(self):
        """
        Creates a table using the line of SQL code provided
        """
        cursor = self.database.cursor()
        cursor.execute(CREATE_TABLE)
        self.database.commit()
