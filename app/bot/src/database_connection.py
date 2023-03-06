import mysql.connector
from config import *


class DatabaseConnection:
    def __init__(self, host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD):
        self._host = host
        self._user = user
        self._password = password
        self._database = MYSQL_DATABASE

    def __enter__(self):
        try:
            self.cnx = mysql.connector.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._database,
                port=MYSQL_PORT
            )
            self.cursor = self.cnx.cursor()
            return self.cursor
        except mysql.connector.Error as e:
            print(f"Error connection: {e}")

    def __exit__(self, t, value, traceback):
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
