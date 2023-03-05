import sqlite3
import base64

QUERY_NEW_USER = "INSERT INTO users(username, password) VALUES(?, ?)"
QUERY_NEW_SCAN = "INSERT INTO scans(payloadURL, result) VALUES(?, ?)"
QUERY_NEW_USERSCAN = "INSERT INTO userScan (userID, scanID) VALUES(?, ?)"


class DBControl:
    def __init__(self):
        self.conn = sqlite3.connect("../database.db")
        self.cursor = self.conn.cursor()

    # Encodes passwords for the users table
    def __encode_passwd(self, passwd):
        return base64.b64encode(passwd.encode()).decode()

    def execute_query(self, query):
        self.cursor.execute(query)

    # Adds user to the users table
    def add_user(self, login, passwd):
        password = self.__encode_passwd(passwd)
        self.cursor.execute(QUERY_NEW_USER, (login, password))
        self.conn.commit()

    # Checks whether user if in the database(used to log in)
    def check_user(self, login, passwd):
        password = self.__encode_passwd(passwd)
        self.cursor.execute(f"SELECT userID FROM users WHERE username = '{login}' AND password = '{password}'")
        result = self.cursor.fetchone()
        if result is None:
            return False
        # Returns userID
        return result[0]

    # Adds a new scan record
    def add_scan(self, userID, results):
        for data in results:
            result = data[0]
            payload_url = data[1]
            self.cursor.execute(QUERY_NEW_SCAN, (payload_url, result))
            scanID = self.cursor.lastrowid
            self.cursor.execute(QUERY_NEW_USERSCAN, (userID, scanID))
        self.conn.commit()

    # Get all urls:result pairs of a user
    def get_user_scan(self, userID):
        self.cursor.execute(f"SELECT payloadURL, result FROM scans, userScan WHERE userScan.userID = '{userID}' "
                            f"AND userScan.scanID = scans.scanID")
        return self.cursor.fetchall()

    # Get a result of a certain scan
    def get_result_scan(self, url):
        self.cursor.execute(f"SELECT result FROM scans WHERE payloadURL = '{url}'")
        return self.cursor.fetchall()

if __name__ == "__main__":
    d = DBControl()
    # print(d.cursor.execute("ALTER TABLE scans RENAME COLUMN startURL TO payloadURL"))
    # print(d.cursor.fetchall())
    # d.add_scan(0, [[2, "test2"], [3, "test3"]])
    d.cursor.execute("DELETE FROM scans")
    # d.cursor.execute("SELECT * FROM userScan")
    d.conn.commit()
    # print(d.check_user("admin", "secret"))
    # print(d.get_user_scan(0))
    # print(d.get_result_scan("test2"))
    # print(d.cursor.fetchall())
    d.conn.close()
