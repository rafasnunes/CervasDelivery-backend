from flask import Flask, request, jsonify, render_template
import sqlite3
import os

# Configuração do Flask
app = Flask(
    __name__,
    template_folder='../frontend/templates',  # Apontando para o front-end
    static_folder='../frontend/static'       # Apontando para os arquivos estáticos
)

# ============================
# Configuração do banco de dados único
# ============================
DATABASE = os.path.join(os.path.dirname(__file__), 'cervasdelivery.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============================
# Rota para página inicial
# ============================
@app.route('/')
def index():
    return render_template('index.html')

# ============================
# Rotas para Clientes
# ============================
@app.route('/clientes-page')
def clientes_page():
    return render_template('clientes.html')

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    conn = get_db_connection()
    if request.method == 'GET':
        clients = conn.execute('SELECT * FROM pessoa').fetchall()
        conn.close()
        return jsonify([dict(row) for row in clients])
    elif request.method == 'POST':
        data = request.json
        try:
            conn.execute('''
                INSERT INTO pessoa (cpf, nome, telefone, logradouro, numero, complemento, cep, bairro, cidade, uf)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cpf) DO UPDATE SET
                    nome=excluded.nome,
                    telefone=excluded.telefone,
                    logradouro=excluded.logradouro,
                    numero=excluded.numero,
                    complemento=excluded.complemento,
                    cep=excluded.cep,
                    bairro=excluded.bairro,
                    cidade=excluded.cidade,
                    uf=excluded.uf;
            ''', (data['cpf'], data['nome'], data['telefone'], data['logradouro'], data['numero'],
                  data.get('complemento', ''), data['cep'], data['bairro'], data['cidade'], data['uf']))
            conn.commit()
            return jsonify({'message': 'Cliente salvo com sucesso!'}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()

@app.route('/clientes/<cpf>', methods=['GET', 'DELETE'])
def get_or_delete_cliente(cpf):
    conn = get_db_connection()
    try:
        if request.method == 'GET':
            client = conn.execute('SELECT * FROM pessoa WHERE cpf = ?', (cpf,)).fetchone()
            if client is None:
                return jsonify({'error': 'Cliente não encontrado'}), 404
            return jsonify(dict(client)), 200
        elif request.method == 'DELETE':
            conn.execute('DELETE FROM pessoa WHERE cpf = ?', (cpf,))
            conn.commit()
            return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# ============================
# Rotas para Cervejas
# ============================
@app.route('/cervejas-page')
def cervejas_page():
    return render_template('cervejas.html')

@app.route('/cervejas', methods=['GET', 'POST'])
def cervejas():
    conn = get_db_connection()
    if request.method == 'GET':
        beers = conn.execute('SELECT * FROM cerveja').fetchall()
        conn.close()
        return jsonify([dict(row) for row in beers])
    elif request.method == 'POST':
        data = request.json
        try:
            conn.execute('''
                INSERT INTO cerveja (cod_barra, nome, marca, tipo, pais, preco)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(cod_barra) DO UPDATE SET
                    nome=excluded.nome,
                    marca=excluded.marca,
                    tipo=excluded.tipo,
                    pais=excluded.pais,
                    preco=excluded.preco;
            ''', (data['cod_barra'], data['nome'], data['marca'], data['tipo'], data['pais'], data['preco']))
            conn.commit()
            return jsonify({'message': 'Cerveja salva com sucesso!'}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()

@app.route('/cervejas/<cod_barra>', methods=['GET', 'DELETE'])
def get_or_delete_cerveja(cod_barra):
    conn = get_db_connection()
    try:
        if request.method == 'GET':
            cerveja = conn.execute('SELECT * FROM cerveja WHERE cod_barra = ?', (cod_barra,)).fetchone()
            if not cerveja:
                return jsonify({'error': 'Cerveja não encontrada'}), 404
            return jsonify(dict(cerveja)), 200
        elif request.method == 'DELETE':
            conn.execute('DELETE FROM cerveja WHERE cod_barra = ?', (cod_barra,))
            conn.commit()
            return jsonify({'message': 'Cerveja excluída com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# ============================
# Rotas para Vendas
# ============================
@app.route('/venda')
def venda_page():
    return render_template('venda.html')

@app.route('/vendas', methods=['POST'])
def finalizar_venda():
    data = request.json
    try:
        # Verificar se os dados necessários estão presentes
        client = data.get('client')
        items = data.get('items')

        if not client:
            return jsonify({'error': 'Cliente não informado'}), 400
        if not items or not isinstance(items, list):
            return jsonify({'error': 'Itens da venda não informados ou no formato incorreto'}), 400

        # Conectar ao banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        # Inserir a venda na tabela de vendas
        cursor.execute('INSERT INTO venda (cliente_id, data_hora) VALUES (?, datetime("now"))', (client,))
        venda_id = cursor.lastrowid

        # Inserir itens da venda
        for item in items:
            if 'cod' not in item or 'quantity' not in item or 'price' not in item:
                return jsonify({'error': 'Dados do item incompletos'}), 400
            cursor.execute(
                '''
                INSERT INTO venda_item (venda_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                ''', (venda_id, item['cod'], item['quantity'], item['price'])
            )

        conn.commit()
        conn.close()

        return jsonify({'message': 'Venda finalizada com sucesso!', 'venda_id': venda_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vendas', methods=['GET'])
def buscar_vendas():
    query = request.args.get('query', '').lower()
    try:
        conn = get_db_connection()
        vendas = conn.execute('''
            SELECT v.id, v.data_hora, c.nome AS cliente_nome, v.status,
                   SUM(vi.quantidade * vi.preco_unitario) AS total
            FROM venda v
            LEFT JOIN venda_item vi ON v.id = vi.venda_id
            LEFT JOIN pessoa c ON v.cliente_id = c.cpf
            WHERE LOWER(c.nome) LIKE ? 
               OR CAST(v.id AS TEXT) LIKE ? 
               OR LOWER(c.cpf) LIKE ?
               OR DATE(v.data_hora) LIKE ?
            GROUP BY v.id
        ''', (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()

        return jsonify([dict(venda) for venda in vendas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vendas/<int:venda_id>', methods=['GET'])
def buscar_detalhes_venda(venda_id):
    try:
        conn = get_db_connection()
        venda = conn.execute('''
            SELECT v.id, v.data_hora, c.nome AS cliente_nome, 
                   SUM(vi.quantidade * vi.preco_unitario) AS total
            FROM venda v
            LEFT JOIN pessoa c ON v.cliente_id = c.cpf
            LEFT JOIN venda_item vi ON v.id = vi.venda_id
            WHERE v.id = ?
            GROUP BY v.id
        ''', (venda_id,)).fetchone()

        if not venda:
            return jsonify({'error': 'Venda não encontrada'}), 404

        itens = conn.execute('''
            SELECT vi.quantidade, vi.preco_unitario, 
                   cerveja.nome AS produto_nome
            FROM venda_item vi
            INNER JOIN cerveja ON vi.produto_id = cerveja.cod_barra
            WHERE vi.venda_id = ?
        ''', (venda_id,)).fetchall()

        conn.close()

        return jsonify({
            'venda': dict(venda),
            'itens': [dict(item) for item in itens]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vendas/<int:sale_id>/cancelar', methods=['POST'])
def cancelar_venda(sale_id):
    try:
        conn = get_db_connection()
        conn.execute('UPDATE venda SET status = "cancelada" WHERE id = ?', (sale_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Venda cancelada com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
