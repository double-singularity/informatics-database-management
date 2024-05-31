import pymysql

class Database:

    def __init__(self) -> None:
        self.db = None
        self.cursor = None

        try:
            db = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="mahasiswaDB"
            )
            print("Connection successful")

            self.cursor = db.cursor()

        except pymysql.MySQLError as e:
            print(f"Error connecting to database: {e}")

    def __del__(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()

    def exec(self, string):
        if self.cursor:
            self.cursor.execute(string)
            return self.cursor
        else:
            print("Cursor not initialized")
            return None
