from utils.Connector import Connector
from utils.AESCipher import encrypt, decrypt

class Users(Connector):
    def __init__(self, page_config):
        super().__init__()
        page_config.set(info_db_connection = self.db_connection)
    
    def signin(self, email, password):
        sql = "SELECT * FROM users WHERE email=%s"
        self.cursor.execute(sql, (email, ))
        result = self.cursor.fetchone()
        
        if result is None:
            return False, False
        
        if decrypt(result[2]).decode("utf-8") == password:
            if result[0] == 1:
                return True, True
            else:
                return True, False
        else:
            return False, False

    def is_root(self, email):
        sql = "SELECT * FROM users WHERE email=%s"
        self.cursor.execute(sql, (self, ))
        result = self.cursor.fetchone()
        
        if result is None:
            return False
        
        if result[0] == 1:
            return True
        else:
            return False

    def root_exist(self):
        sql = "SELECT * FROM users WHERE root=1"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()

        if result is not None:
            return True
        else: 
            return False

    def signup(self, root, email, password):
        sql = "INSERT INTO users (root, email, password) values (%s, %s, %s)"
        self.cursor.execute(sql, (root, email, encrypt(password)))
        self.conn.commit()
        
    def __del__(self):
        self.close()