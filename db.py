import pymysql

try:
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="",
    )

    print("Connection successful")

except pymysql.MySQLError as e:
    print(f"Error connecting to database: {e}")


cursor = db.cursor()
cursor.execute("SHOW DATABASES;")


# Closing the cursor and connection to the database
cursor.close()
db.close()