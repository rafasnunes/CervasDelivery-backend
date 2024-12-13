import sqlite3

# Função para conectar ao banco de dados
def conectar_banco(nome_banco):
    try:
        conexao = sqlite3.connect(nome_banco)
        return conexao
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados {nome_banco}: {e}")
        return None
