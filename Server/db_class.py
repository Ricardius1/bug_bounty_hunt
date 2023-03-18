import sqlite3
import base64

QUERY_NEW_USER = "INSERT INTO users(username, password) VALUES(?, ?)"
QUERY_NEW_SCAN = "INSERT INTO scans(payloadURL, result) VALUES(?, ?)"
QUERY_NEW_USERSCAN = "INSERT INTO userScan (userID, scanID) VALUES(?, ?)"

"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""Controlling all database operations"""


class DBControl:
    def __init__(self):
        self.conn = sqlite3.connect("../database.db")
        self.cursor = self.conn.cursor()

    # Encodes passwords for the users table
    # I wanted to show that when storing passwords in the database they have to be hidden(encoded) in some way
    # to prevent from loss of passwords
    def __encode_passwd(self, passwd):
        return base64.b64encode(passwd.encode()).decode()

    # Adds user to the users table
    def add_user(self, login, passwd):
        # Encoding the password
        password = self.__encode_passwd(passwd)
        # Sending the command to the database to save the user record
        self.cursor.execute(QUERY_NEW_USER, (login, password))
        self.conn.commit()

    # Checks whether user if in the database(used to log in)
    def check_user(self, login, passwd):
        # Encode the password to check for it
        password = self.__encode_passwd(passwd)
        # Use SELECT query to check if there is a record on a specific user
        self.cursor.execute(f"SELECT userID FROM users WHERE username = '{login}' AND password = '{password}'")
        result = self.cursor.fetchone()
        # Checking the result from the database
        if result is None:
            return False
        # Returns userID
        return result[0]

    # Adds a new scan record
    def add_scan(self, userID, results):
        # Add all the positive scans to the table scans and add a record to the userScan link table
        for data in results:
            result = data[0]
            payload_url = data[1]
            # Adding record to the scans table
            self.cursor.execute(QUERY_NEW_SCAN, (payload_url, result))
            # get the last scanID
            scanID = self.cursor.lastrowid
            # Add record to the userScan table
            self.cursor.execute(QUERY_NEW_USERSCAN, (userID, scanID))
        # Commit all the changes
        self.conn.commit()

    # Get all urls:result pairs of a user
    def get_user_scan(self, userID):
        # Get all the scans performed by the user
        self.cursor.execute(f"SELECT payloadURL, result FROM scans, userScan WHERE userScan.userID = '{userID}' "
                            f"AND userScan.scanID = scans.scanID")
        return self.cursor.fetchall()

    # Get a result of a certain scan
    def get_result_scan(self, url):
        # Get the result of a specified scan
        self.cursor.execute(f"SELECT result FROM scans WHERE payloadURL = '{url}'")
        return self.cursor.fetchall()


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""

