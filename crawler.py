import requests
from bs4 import BeautifulSoup
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Hridyesh@123",
        database="isid_db"
    )

url = "https://ngodarpan.gov.in/index.php/search"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# ⚠️ This is demo scraping (structure may vary)
rows = soup.find_all("tr")

conn = get_db_connection()
cursor = conn.cursor()

for row in rows:
    cols = row.find_all("td")
    
    if len(cols) > 2:
        title = cols[0].text.strip()
        state = cols[1].text.strip()

        try:
            cursor.execute(
                "INSERT INTO projects (title, source, url, state, category, country, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (title, "NGO from Darpan", "", state, "General", "India", "Active")
            )
        except:
            pass

conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully!")