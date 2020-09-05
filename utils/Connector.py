from mysql.connector import connect, Error
from utils.Settings import host, database, user, password

class Connector:
    def __init__(self):
        self.conn = None
        try:
            self.conn = connect(
                host = host,
                database = database,
                user = user, 
                password = password,
        )
        except Error as e:
            print("[connect error: {}]".format(e))

        self.db_connection = True
        if self.conn is not None:
            self.cursor = self.conn.cursor()
        else:
            self.db_connection = False

    def close(self):
        self.cursor.close(); self.conn.close()

    def __del__(self):
        self.close()