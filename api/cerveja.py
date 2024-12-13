import sqlite3
from typing import List, Optional

class Cerveja:
    def __init__(self, cod_barra, nome, marca, tipo, pais, preco):
        self.cod_barra = cod_barra
        self.nome = nome
        self.marca = marca
        self.tipo = tipo
        self.pais = pais
        self.preco = preco

class CervejaDAO:
    def __init__(self, db_path: str = 'cerveja.db'):
        self.db_path = db_path
        self.criar_tabelas()
    
    def criar_tabelas(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cerveja (
                cod_barra TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                marca TEXT NOT NULL,
                tipo TEXT NOT NULL,
                pais TEXT NOT NULL,
                preco REAL NOT NULL
            )
            """)
            conn.commit()
    
    def salvar_cerveja(self, cerveja):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO cerveja (cod_barra, nome, marca, tipo, pais, preco)
                VALUES (?,?,?,?,?,?)""", (cerveja.cod_barra, cerveja.nome, cerveja.marca, cerveja.tipo, cerveja.pais, cerveja.preco))

                conn.commit()
                print(f"Cerveja {cerveja.nome} salva com sucesso!")
        except sqlite3.Error as e:
            print(f'Erro ao salvar cerveja: {e}')
    
    def buscar_cod_barra(self, cod_barra: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT *
                FROM cerveja
                WHERE cod_barra = ?""", (cod_barra,))

                resultado = cursor.fetchone()

                if resultado:
                    return Cerveja(*resultado)
                else:
                    print(f"Nenhuma cerveja encontrada com o Código de Barras {cod_barra}")
                    return None
        except sqlite3.Error as e:
            print(f"Erro ao buscar cerveja: {e}")
            return None
    
    def listar_cerveja(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT *
                FROM cerveja""")

                resultados = cursor.fetchall()
                return [Cerveja(*resultado) for resultado in resultados]
        except sqlite3.Error as e:
            print(f"Erro ao listar cervejas: {e}")
            return []
    
    def deletar_cerveja(self, cod_barra: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cerveja WHERE cod_barra=?', (cod_barra,))

                if cursor.rowcount > 0:
                    print(f"Cerveja {cod_barra} deletada com sucesso!")
                else:
                    print(f"Nenhuma cerveja encontrada com o código {cod_barra}!")
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao deletar cerveja: {e}")

def main():
    dao = CervejaDAO()

    # Criar nova cerveja
    nova_cerveja = Cerveja(
        cod_barra='7896004234590',
        nome='Heineken Puro Malte Lager Premium Long-Neck 330ml',
        marca='Heineken',
        tipo='Lager',
        pais='Holanda',
        preco=8.99,
    )

    dao.salvar_cerveja(nova_cerveja)

    # Buscar cerveja por código de barras
    cerveja_buscada = dao.buscar_cod_barra('7896004234590')
    if cerveja_buscada:
        print(f"Cerveja encontrada: {cerveja_buscada.nome}")
    
    # Listar todas as cervejas
    cervejas = dao.listar_cerveja()
    for cerveja in cervejas:
        print(f"Cod. Barra: {cerveja.cod_barra}, Nome: {cerveja.nome}")

if __name__ == '__main__':
    main()
