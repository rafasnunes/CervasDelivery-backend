import sqlite3
from typing import List, Optional

class venda:
    def __init__(self, id_venda, data, cpf, pgto, total_venda):
        self.id_venda = id_venda
        self.data = data
        self.cpf = cpf
        self.pgto = pgto
        self.total_venda = total_venda

class VendaDAO:
    def __init__(self, db_path: str = 'venda.db'):
        self.db_path = db_path
        self.criar_tabelas()
    
    def criar_tabelas(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cpf TEXT NOT NULL,
                pgto BOOLEAN NOT NULL DEFAULT 0,
                total_venda REAL NOT NULL,
                FOREIGN KEY (cpf) REFERENCES pessoa(cpf)
            )
            """)
            conn.commit()

def main():
    dao = VendaDAO()

if __name__ == '__main__':
    main()