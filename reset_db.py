import sqlite3

conn = sqlite3.connect("despesas.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS despesas")

cursor.execute("""
CREATE TABLE despesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT NOT NULL,
    data TEXT NOT NULL,
    valor REAL NOT NULL,
    descricao TEXT
)
""")

conn.commit()
conn.close()

print("Banco de dados resetado com tabela despesas limpa.")
