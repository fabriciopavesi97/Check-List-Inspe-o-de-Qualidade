import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

INSPETORES = ["Inspetor 1", "Inspetor 2", "Inspetor 3", "Inspetor 4"]
LOCAIS_INSPECAO = ["Externa", "Ibirama", "Brusque"]
TAMANHOS = [
    "PP", "P", "M", "G", "EG", "EGG", "PE", "ME", "GR", "XG",
    "1", "2", "3", "4", "6", "8", "10", "12", "14", "16", "18", "U"
]
DEFEITOS = [
    "Alça Torcida", "Diferença de cavas", "Arremate com bolinha", "Arremate desencontrado",
    "Bainha cortada", "Bainha desencontrada", "Bainha torcida/enviasada", "Rebarba de bainha",
    "Bainha com bananinha", "Biquinho decote fora do centro", "Biquinho decote com acabamento mal feito",
    "Costura enrrugada", "Costura escapada", "Costura estourada", "Costura torta", "Emenda na costura",
    "Furo de agulha (na peça e etiqueta)", "Linha do Franzido aparecendo", "Marca de costura desmanchada",
    "Peitilho torto", "Ponto falhado", "Prega na costura", "Regulagem de ponto", "Viés caído",
    "Casamento de recortes", "Falta travete", "Viés escapado", "Bolsos Tortos", "Lacinho mal pregado",
    "Peça sem lacinho", "Peça cortada", "Sobra de fios Costura", "Cós escapado", "Falso amarrador mal costurado",
    "Falso amarrador no lugar errado", "Composição errada", "Etiqueta errada", "Etiqueta de tamanho trocada",
    "Etiqueta lado errado", "Etiqueta torta", "Peça sem etiqueta", "Transfer com tamanho errado",
    "Transfer falhado", "Transfer fora do centro", "Transfer descolando", "Sujeiras", "Peça molhada",
    "Manchas", "Óleo de costura", "Barramento", "Óleo de Tinturaria", "Contaminação / fibras estranhas",
    "Tonalidade", "Torção", "Vinco", "Desencaixe de estampa", "Estampa falhada", "Emenda Materia prima",
    "Marcação do final do rolo", "Furo de malha", "Decote franzido", "Decote esgaçado", "Medidas (fora tolerância)"
]

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS checklist_qualidade (
                id SERIAL PRIMARY KEY,
                data_inspecao DATE,
                inspetor VARCHAR(100),
                fornecedor VARCHAR(150),
                nr_op VARCHAR(50),
                familia VARCHAR(100),
                referencia_prod VARCHAR(100),
                local_inspecao VARCHAR(50),
                qtd_prontas INT,
                qtd_inspecionadas INT,
                tamanho VARCHAR(20),
                defeito VARCHAR(150),
                qtd_defeitos INT,
                observacao TEXT,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")

init_db()

@app.route('/', methods=['GET'])
def index():
    sucesso = request.args.get('sucesso')
    edit_id = request.args.get('edit_id')
    registro = None

    if edit_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, data_inspecao, inspetor, fornecedor, nr_op, familia, referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas, tamanho, defeito, qtd_defeitos, observacao FROM checklist_qualidade WHERE id = %s;", (edit_id,))
        registro = cur.fetchone()
        cur.close()
        conn.close()

    return render_template(
        'index.html', 
        inspetores=INSPETORES, 
        locais=LOCAIS_INSPECAO, 
        tamanhos=TAMANHOS, 
        defeitos=DEFEITOS,
        sucesso=sucesso,
        registro=registro
    )

@app.route('/salvar', methods=['POST'])
def salvar():
    registro_id = request.form.get('registro_id')
    data_inspecao = request.form.get('data_inspecao')
    inspetor = request.form.get('inspetor')
    fornecedor = request.form.get('fornecedor')
    nr_op = request.form.get('nr_op')
    familia = request.form.get('familia')
    referencia_prod = request.form.get('referencia_prod')
    local_inspecao = request.form.get('local_inspecao')
    qtd_prontas = request.form.get('qtd_prontas') or 0
    qtd_inspecionadas = request.form.get('qtd_inspecionadas') or 0
    observacao = request.form.get('observacao')

    tamanhos = request.form.getlist('tamanho[]')
    lista_defeitos = request.form.getlist('defeito[]')
    qtds_defeitos = request.form.getlist('qtd_defeitos[]')

    conn = get_db_connection()
    cur = conn.cursor()

    # Se estiver editando um registro existente
    if registro_id:
        # Atualiza o primeiro item com o ID existente
        if len(tamanhos) > 0 and lista_defeitos[0]:
            cur.execute('''
                UPDATE checklist_qualidade SET
                    data_inspecao = %s, inspetor = %s, fornecedor = %s, nr_op = %s, 
                    familia = %s, referencia_prod = %s, local_inspecao = %s, 
                    qtd_prontas = %s, qtd_inspecionadas = %s, tamanho = %s, 
                    defeito = %s, qtd_defeitos = %s, observacao = %s
                WHERE id = %s
            ''', (
                data_inspecao, inspetor, fornecedor, nr_op, familia,
                referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas,
                tamanhos[0], lista_defeitos[0], qtds_defeitos[0] or 0, observacao, registro_id
            ))
    else:
        # Criação normal (inserindo novos)
        for tam, def_, qtd_def in zip(tamanhos, lista_defeitos, qtds_defeitos):
            if def_:
                cur.execute('''
                    INSERT INTO checklist_qualidade (
                        data_inspecao, inspetor, fornecedor, nr_op, familia, 
                        referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas, 
                        tamanho, defeito, qtd_defeitos, observacao
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    data_inspecao, inspetor, fornecedor, nr_op, familia,
                    referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas,
                    tam, def_, qtd_def or 0, observacao
                ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('index', sucesso=1))

@app.route('/historico', methods=['GET'])
def historico():
    conn = get_db_connection()
    cur = conn.cursor()
    # Sem limite (ilimitado) ordenado do mais recente para o mais antigo
    cur.execute("SELECT id, data_inspecao, inspetor, fornecedor, nr_op, referencia_prod, tamanho, defeito, qtd_defeitos FROM checklist_qualidade ORDER BY id DESC;")
    registros = cur.fetchall()
    cur.close()
    conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Histórico de Inspeções</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 30px; background: #f0f2f5; color: #333; }
            .container { max-width: 1100px; margin: 0 auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            h2 { color: #1e293b; margin-top: 0; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #e2e8f0; padding: 10px 12px; text-align: left; font-size: 13px; }
            th { background-color: #3b82f6; color: white; }
            tr:nth-child(even) { background-color: #f8fafc; }
            .btn-voltar { display: inline-block; padding: 10px 18px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; transition: background 0.2s; }
            .btn-voltar:hover { background: #2563eb; }
            .btn-editar { padding: 5px 10px; background: #f59e0b; color: white; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 12px; }
            .btn-editar:hover { background: #d97706; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📊 Histórico de Inspeções (Completo e Ilimitado)</h2>
            <p style="color: #64748b; font-size: 14px;">Todos os registros salvos na nuvem.</p>
            <a href="/" class="btn-voltar">← Voltar para o Formulário</a>
            <table>
                <tr>
                    <th>Data</th>
                    <th>Inspetor</th>
                    <th>Fornecedor</th>
                    <th>N° OP</th>
                    <th>Referência</th>
                    <th>Tamanho</th>
                    <th>Defeito</th>
                    <th>Qtd</th>
                    <th>Ações</th>
                </tr>
    '''
    for reg in registros:
        html += f"<tr><td>{reg[1]}</td><td>{reg[2]}</td><td>{reg[3]}</td><td>{reg[4]}</td><td>{reg[5]}</td><td>{reg[6]}</td><td>{reg[7]}</td><td>{reg[8]}</td><td><a href='/?edit_id={reg[0]}' class='btn-editar'>✏️ Editar</a></td></tr>"
    
    html += '''
            </table>
        </div>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
