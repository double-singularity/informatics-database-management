import pymysql

class Database:
    def __init__(self, host="localhost", user="root", password="", database="mahasiswaDB"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Connected to the database.")
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from the database.")
        else:
            print("Not connected to any database.")

    def execute_query(self, query, values=None):
        try:
            with self.connection.cursor() as cursor:
                if values:
                    cursor.execute(query, values)
                else:
                    cursor.execute(query)
                self.connection.commit()
                print("Query executed successfully.")
        except Exception as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()

    def fetch_data(self, query, values=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                return [dict(zip(column_names, row)) for row in result]
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

