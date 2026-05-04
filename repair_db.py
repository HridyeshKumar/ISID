import sqlite3

# corrupted database
corrupt_db = "database.db"

# repaired database
new_db = "recovered.db"

try:
    conn = sqlite3.connect(corrupt_db)
    cursor = conn.cursor()

    # dump entire database
    dump = "\n".join(conn.iterdump())

    conn.close()

    # create fresh database
    new_conn = sqlite3.connect(new_db)
    new_cursor = new_conn.cursor()

    # rebuild database
    new_conn.executescript(dump)

    new_conn.commit()
    new_conn.close()

    print("✅ Database recovered successfully")

except Exception as e:
    print("❌ Recovery failed:", e)