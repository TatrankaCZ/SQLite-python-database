import mysql.connector

db = mysql.connector.connect(**{
  'user': 'admin',
  'password': 'admin',
  'host': '127.0.0.1',
  'port': '3306',
  'database': 'numberguessingdb'
})

cursor = db.cursor()

cursor.execute("CREATE DATABASE numberguessingdb;")

cursor.execute("USE numberguessingdb;")

cursor.execute("CREATE TABLE game_scores (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), score INT);")
