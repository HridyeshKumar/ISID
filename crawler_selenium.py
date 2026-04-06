from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Hridyesh@123",
        database="isid_db"
    )

driver = webdriver.Chrome()
driver.get("https://ngodarpan.gov.in/index.php/search")

time.sleep(5)

conn = get_db_connection()
cursor = conn.cursor()

# 🔥 Loop through pages
for page in range(1, 6):  # change to 50 later

    print(f"Scraping page {page}...")

    table = driver.find_element(By.TAG_NAME, "table")
    rows = table.find_elements(By.TAG_NAME, "tr")

    for row in rows[1:]:  # skip header
        cols = row.find_elements(By.TAG_NAME, "td")

        if len(cols) >= 2:
            title = cols[0].text.strip()
            state = cols[1].text.strip()

            if title and state and len(title) < 100:  # avoid garbage
                try:
                    cursor.execute(
                        "INSERT INTO projects (title, source, url, state, category, country, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (title, "NGO Darpan", "", state, "General", "India", "Active")
                    )
                except:
                    pass

    # 🔥 Click next button
    try:
        next_btn = driver.find_element(By.XPATH, "//a[contains(text(),'Next')]")
        next_btn.click()
        time.sleep(3)
    except:
        print("No more pages")
        break

conn.commit()
cursor.close()
conn.close()

driver.quit()

print("Title:", title, "| State:", state)