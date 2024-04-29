import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Aneesh123",
  database = "the_app"
)

mycursor = mydb.cursor()

mycursor.execute("select * from users")

myresult = mycursor.fetchall()




