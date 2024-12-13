import sqlite3
from typing import List, Optional

class pedido:
    def __init__(self, id_pedido, id_venda, quantidade, cod_barra, preco, total_pedido):
        self.id_pedido = id_pedido
        self.id_venda = id_venda
        self.quantidade = quantidade
        self.cod_barra = cod_barra
        self.preco = preco
        self.total_pedido = total_pedido

class PedidoDAO:
    def __init__(self, db_path: str = 'pedido.db'):
        self.db_path = db_path
        self.criar_tabelas()
    
    def criar_tabelas(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedido (
                id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venda INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                cod_barra INTEGER NOT NULL,
                preco REAL NOT NULL,
                total_comanda REAL NOT NULL,
                FOREIGN KEY (id_venda) REFERENCES vendas(id_venda),
                FOREIGN KEY (cod_barra) REFERENCES cerveja(cod_barra),
                FOREIGN KEY (preco) REFERENCES cerveja(preco)
            )
            """)
            conn.commit()

def main():
    dao = PedidoDAO()

if __name__ == '__main__':
    main()