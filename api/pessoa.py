import sqlite3

DATABASE = 'pessoa.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabela_pessoa():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pessoa (
            cpf CHAR(14) PRIMARY KEY NOT NULL, -- CPF formatado como XXX.XXX.XXX-XX
            nome VARCHAR(100) NOT NULL,        -- Nome completo
            telefone CHAR(15) NOT NULL,        -- Telefone no formato (XX) XXXXX-XXXX
            logradouro VARCHAR(100) NOT NULL, -- Endereço
            numero VARCHAR(10) NOT NULL,      -- Número da residência
            complemento VARCHAR(50) NOT NULL, -- Complemento do endereço
            cep CHAR(9) NOT NULL,             -- CEP no formato XXXXX-XXX
            bairro VARCHAR(50) NOT NULL,      -- Bairro
            cidade VARCHAR(50) NOT NULL,      -- Cidade
            uf CHAR(2) NOT NULL               -- UF com 2 caracteres
);
    ''')
    conn.commit()
    conn.close()

def adicionar_pessoa(cpf, nome, telefone, logradouro, numero, complemento, cep, bairro, cidade, uf):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO pessoa (cpf, nome, telefone, logradouro, numero, complemento, cep, bairro, cidade, uf)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cpf, nome, telefone, logradouro, numero, complemento, cep, bairro, cidade, uf))
    conn.commit()
    conn.close()

def editar_pessoa(cpf, nome, telefone, logradouro, numero, complemento, cep, bairro, cidade, uf):
    conn = get_db_connection()
    conn.execute('''
        UPDATE pessoa
        SET nome = ?, telefone = ?, logradouro = ?, numero = ?, complemento = ?, cep = ?, bairro = ?, cidade = ?, uf = ?
        WHERE cpf = ?
    ''', (nome, telefone, logradouro, numero, complemento, cep, bairro, cidade, uf, cpf))
    conn.commit()
    conn.close()

def excluir_pessoa(cpf):
    conn = get_db_connection()
    conn.execute('DELETE FROM pessoa WHERE cpf = ?', (cpf,))
    conn.commit()
    conn.close()

def buscar_pessoas():
    conn = get_db_connection()
    pessoas = conn.execute('SELECT * FROM pessoa').fetchall()
    conn.close()
    return [dict(pessoa) for pessoa in pessoas]

def buscar_pessoa_por_cpf(cpf):
    conn = get_db_connection()
    pessoa = conn.execute('SELECT * FROM pessoa WHERE cpf = ?', (cpf,)).fetchone()
    conn.close()
    return dict(pessoa) if pessoa else None