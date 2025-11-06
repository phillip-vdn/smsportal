import pyodbc
import os

db_path = os.path.join(os.path.dirname(__file__), "test.mdb")
conn = pyodbc.connect(
    fr"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
)
cur = conn.cursor()

cur.execute("UPDATE Invoice SET [Addr1] = ? WHERE TxnNo = ?", ("Test", 127285))
print(f"Rows updated: {cur.rowcount}")

conn.commit()

cur.execute("SELECT TOP 5 * FROM Invoice WHERE [Addr1] = ?", ("Test",))
for row in cur.fetchall():
    try:
        print(row)
        
        print(getattr(row, "Patient", None))
        print(getattr(row, "Name", None))
        print(getattr(row, "Addr1", None))
        print(getattr(row, "TxnNo", None))
    except Exception:
        print(row)

conn.close()
