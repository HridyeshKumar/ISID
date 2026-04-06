import pandas as pd
import mysql.connector

df = pd.read_csv("ngo_data.csv")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Hridyesh@123",
    database="isid_db"
)

cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute(
        "INSERT INTO projects (title, source, url, state, category, country, status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        tuple(row)
    )

conn.commit()
cursor.close()
conn.close()

print("CSV data inserted!")