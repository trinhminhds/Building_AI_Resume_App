import pymysql

try:
    connection = pymysql.connect(host='localhost', user='root', password='23092003')
    cursor = connection.cursor()
    # Your database operations here
except pymysql.MySQLError as e:
    print(f"Error connecting to the database: {e}")
finally:
    if connection:
        connection.close()