import mysql.connector

db = mysql.connector.connect(
  host="localhost",
  user="admin",
  password="admin"
)

cursor = db.cursor()

cursor.execute("CREATE DATABASE numberguessingdb;")

cursor.execute("USE numberguessingdb;")

cursor.execute("CREATE TABLE game_scores (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), score INT);")
