import mysql.connector

# Connect to MySQL server
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Database#2010"
)

cursor = conn.cursor()

# Create database if not exists
cursor.execute("CREATE DATABASE IF NOT EXISTS user_auth")
cursor.execute("USE user_auth")

