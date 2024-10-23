import mysql.connector
import json
import secrets
PASSWORD = 'password'
DATABASE = 'products'
SERIAL_LENGTH = 10
AUTOINCREMENT_INDEX = 10
CREATE_TABLE = """
CREATE TABLE products (
  ID INT AUTO_INCREMENT PRIMARY KEY,
  SerialNumber VARCHAR(10) UNIQUE NOT NULL,
  PartNumber VARCHAR(50) DEFAULT 'Unknown',
  DesignVersion INT DEFAULT 0,
  CreationParameters TEXT,
  PurchaseOrder TEXT,
  DeliveryRecords TEXT,
  Feedback TEXT,
  Images TEXT,
  MFGSuccess BOOLEAN DEFAULT FALSE,
  PerfSuccess BOOLEAN DEFAULT FALSE,
  CustomerSuccess BOOLEAN DEFAULT FALSE,
  CriticalFrequency DECIMAL(10, 4) DEFAULT 0,
  Bandwidth DECIMAL(10, 4) DEFAULT 0
  OtherFiles TEXT,
);"""
REQUIRED_KEYS = ['SerialNumber', 'PartNumber', 'DesignVersion', 'CreationParameters', 'PurchaseOrder', 'DeliveryRecords',
                 'Feedback', 'Images', 'MFGSuccess', 'PerfSuccess', 'CustomerSuccess', 'CriticalFrequency', 'Bandwidth']


class Database:
    def __init__(self):
        self.database = None
        self.connect()

    def create_table(self):
        """
        Creates a table using the line of SQL code provided
        """
        cursor = self.database.cursor()
        cursor.execute(CREATE_TABLE)

    def get_item(self, serial):
        """
        Returns the entry associated with the serial number
        """
        if not isinstance(serial, str) or len(serial) != SERIAL_LENGTH:
            return None
        cursor = self.database.cursor()
        cursor.execute(f'SELECT * FROM products WHERE SerialNumber="{serial}"')
        keys = cursor.description
        return dict(zip([key[0] for key in keys], cursor.fetchone()))

    def connect(self):
        """
        Connects to a SQL database
        """
        try:
            self.database = mysql.connector.connect(host='localhost', user='server', password=PASSWORD, database=DATABASE)
        except:
            raise Exception('Could not connect to database')

    def new_serial(self):
        """
        Returns the next available randomly assigned serial number for the filters
        """
        cursor = self.database.cursor()
        query = f'SHOW TABLE STATUS LIKE "{DATABASE}"'
        cursor.execute(query)
        result = cursor.fetchone()
        if result is None:
            return None
        auto_increment = int(result[AUTOINCREMENT_INDEX])
        auto_increment = f'{auto_increment:06}'
        while True:
            serial = secrets.token_hex(2)
            serial += auto_increment
            if not self.serial_exists(serial):
                # Add the new serial number to the database and return
                query = f'INSERT INTO {DATABASE} (SerialNumber) VALUES (%s)'
                cursor.execute(query, (serial,))
                self.database.commit()
                cursor.close()
                return serial

    def serial_exists(self, serial) -> bool:
        """
        Returns True if the serial number exists in the database, False otherwise
        """
        cursor = self.database.cursor()
        query = f'SELECT * FROM {DATABASE} WHERE SerialNumber = "{serial}"'
        cursor.execute(query)
        return cursor.fetchone() is not None

    def edit_item(self, item: dict, serial: str) -> bool:
        return self.add_item(item, serial, check=False)

    def add_item(self, item: dict, serial: str, check: bool = True) -> bool:
        """
        Put the item in the database assuiming that a row with serial number serial has already been created
        """
        if check and not self.check_item(item, serial):
            return False
        cursor = self.database.cursor()
        columns = ', '.join(f'{col}=%s' for col in item.keys())
        print(columns)
        query = f'UPDATE {DATABASE} SET {columns} WHERE SerialNumber="{serial}"'
        print(query)
        try:
            cursor.execute(query, tuple(item.values()))
        except Exception as e:
            print(f'Error: {e}')
            return False
        self.database.commit()
        cursor.close()
        return True

    def check_item(self, item: dict, serial: str) -> bool:
        """
        Check an item against a list of required keys to ensure that it is valid
        """
        return all(key in item for key in REQUIRED_KEYS) and len(serial) == SERIAL_LENGTH
