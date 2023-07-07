import mysql.connector
from config import *
from database_connection import DatabaseConnection


class Database:
    """
    States:
    1. choice doctor
    2. choice date
    3. choice time
    4. send phone
    5. check data
    6. enter name
    7. finish
    8. feedback
    """

    def __init__(self):
        try:
            with DatabaseConnection() as cursor:
                self.connected = True
        except:
            self.connected = False

    def add_user(self, tg_user_id):
        with DatabaseConnection() as cursor:
            try:
                expression = f"DELETE FROM Users WHERE tg_user_id=%s;"
                cursor.execute(expression, (tg_user_id,))

                expression = f"INSERT Users(tg_user_id, state) VALUES (%s, 'choice doctor');"
                cursor.execute(expression, (tg_user_id,))
                return 0
            except Exception as e:
                print(f"Exception in database function: {e}")
                return 1

    def get_state(self, tg_user_id):
        with DatabaseConnection() as cursor:
            try:
                expression = f"SELECT state FROM Users WHERE tg_user_id=%s;"
                cursor.execute(expression, (tg_user_id, ))
                return cursor.fetchall()
            except Exception as e:
                print(f"Exception in database function: {e}")
                return 1

    def update_row(self, tg_user_id, column, value):
        with DatabaseConnection() as cursor:
            try:
                expression = f"UPDATE Users SET {column}=%s WHERE tg_user_id=%s;"
                cursor.execute(expression, (value, tg_user_id))
                return 0
            except Exception as e:
                print(f"Exception in database function: {e}")
                return 1

    def get_column(self, tg_user_id, colomn):
        with DatabaseConnection() as cursor:
            try:
                expression = f"SELECT {colomn} FROM Users WHERE tg_user_id=%s;"
                cursor.execute(expression, (tg_user_id, ))
                return cursor.fetchall()
            except Exception as e:
                print(f"Exception in database function: {e}")
                return 1

    def read_exec(self, expression, params: tuple):
        with DatabaseConnection() as cursor:
            try:
                cursor.execute(expression, params)
                return cursor.fetchall()
            except Exception as e:
                print(f"Exception in database function: {e}")
                return 1
