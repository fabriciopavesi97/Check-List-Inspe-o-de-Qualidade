import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

INSPETORES = ["Inspetor 1", "Inspetor 2", "Inspetor 3", "Inspetor 4"]
LOCAIS_INSPECAO = ["Externa", "Ibirama", "Brusque"]

FORNECEDORES = [
    "ADELI APARECIDA DOS SANTOS - ME", "CRISTIANE SILVA REZINI", "BEATRIZ CAROLINA",
    "SV CONFECCAO LTDA", "ELISON JOAO DEBATIN (Janara)", "FABIANA KANNENBERG",
    "DEJANETE FACCAO LTDA", "OZEAN INDUSTRIA E COMERCIO", "JUREMA CRISTOVAO",
    "LETICIA SCHLINDWE", "JAQUE JS", "JEFFETUR CONFECCOES E TURISMO LTDA - ME",
    "KAROLAIN", "MARIZA SCHURT", "DENILSON DE MENDONCA", "SARA RODRIGUES FRANESI",
    "TAMIRES LONGEN", "EMILLY ELIAS", "EDSON DIETRICH", "CARLOS ZECHNER",
    "ELISA VICTORINO DIETRICH", "MARCIA REGINA DA SILVA", "CLEONICE DA SILVA GOMES",
    "ALEXANDRA KRAUSE", "MARILENE APARECIDA RODRIGUES", "MARIA DE LOURDES DOS SANTOS",
    "ANA PAULA DA SILVA", "ELIANE CRISTINA DE SOUZA", "ROSANGELA APARECIDA",
    "CLAUDIA REGINA SOARES", "LUCIANA DE OLIVEIRA", "JULIANA APARECIDA",
    "VANESSA CRISTINA", "PATRICIA GOMES DA SILVA", "SANDRA REGINA",
    "CAMILA SOUZA", "BEATRIZ SILVEIRA", "FRANCINE PEREIRA", "GIZELI DOS SANTOS",
    "JESSICA EDUARDA", "KARINA SOUZA", "LARISSA LOPES", "MARIANA COSTA",
    "NATALIA OLIVEIRA", "PAMELA RODRIGUES", "QUEZIA SANTOS", "RAQUEL VIEIRA",
    "SABRINA MARTINS", "TATIANE LIMA", "VIVIANE SOUZA", "ALINE FERREIRA",
    "BRUNA CARVALHO", "CARLA MENDES", "DANIELA DIAS", "ELIZABETH ROCHA",
    "FERNANDA LOPES", "GABRIELA RIBEIRO", "HELENA MARTINS", "ISABELA COSTA",
    "JULIA OLIVEIRA", "KAREN SANTOS", "LARISSA SILVA", "MARINA SOUZA",
    "NATALIA LOPES", "PAMELA FERREIRA", "RAFAELA DIAS", "SABRINA ROCHA", "TATIANE SILVA"
]

TAMANHOS = [
    "PP", "P", "M", "G", "EG", "EGG", "PE", "ME", "GR", "XG",
    "1", "2", "3", "4", "6", "8", "10", "12", "14", "16", "18", 
    "40", "42", "44", "46", "48", "50", "U"
]

DEFEITOS = [
    "Nenhum Defeito Encontrado (Lote Perfeito)",
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
                hora_inicio TIME,
                hora_fim TIME,
                status_lote VARCHAR(20),
                observacao TEXT,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        cur.execute("ALTER TABLE checklist_qualidade ADD COLUMN IF NOT EXISTS hora_inicio TIME;")
        cur.execute("ALTER TABLE checklist_qualidade ADD COLUMN IF NOT EXISTS hora_fim TIME;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar/atualizar tabela: {e}")

init_db()

@app.route('/', methods=['GET'])
def index():
    sucesso = request.args.get('sucesso')
    edit_id = request.args.get('edit_id')
    registro = None

    if edit_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, data_inspecao, inspetor, fornecedor, nr_op, familia, referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas, tamanho, defeito, qtd_defeitos, hora_inicio, hora_fim, status_lote, observacao FROM checklist_qualidade WHERE id = %s;", (edit_id,))
        registro = cur.fetchone()
        cur.close()
        conn.close()

    return render_template(
        'index.html', 
        inspetores=INSPETORES, 
        locais=LOCAIS_INSPECAO, 
        fornecedores=FORNECEDORES,
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
    hora_inicio = request.form.get('hora_inicio') or None
    hora_fim = request.form.get('hora_fim') or None
    status_lote = request.form.get('status_lote')
    observacao = request.form.get('observacao')

    tamanhos = request.form.getlist('tamanho[]')
    lista_defeitos = request.form.getlist('defeito[]')
    qtds_defeitos = request.form.getlist('qtd_defeitos[]')

    conn = get_db_connection()
    cur = conn.cursor()

    if registro_id:
        if len(tamanhos) > 0 and lista_defeitos[0]:
            cur.execute('''
                UPDATE checklist_qualidade SET
                    data_inspecao = %s, inspetor = %s, fornecedor = %s, nr_op = %s, 
                    familia = %s, referencia_prod = %s, local_inspecao = %s, 
                    qtd_prontas = %s, qtd_inspecionadas = %s, tamanho = %s, 
                    defeito = %s, qtd_defeitos = %s, hora_inicio = %s, hora_fim = %s, 
                    status_lote = %s, observacao = %s
                WHERE id = %s
            ''', (
                data_inspecao, inspetor, fornecedor, nr_op, familia,
                referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas,
                tamanhos[0], lista_defeitos[0], qtds_defeitos[0] or 0, hora_inicio, hora_fim, status_lote, observacao, registro_id
            ))
    else:
        for tam, def_, qtd_def in zip(tamanhos, lista_defeitos, qtds_defeitos):
            if def_:
                cur.execute('''
                    INSERT INTO checklist_qualidade (
                        data_inspecao, inspetor, fornecedor, nr_op, familia, 
                        referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas, 
                        tamanho, defeito, qtd_defeitos, hora_inicio, hora_fim, status_lote, observacao
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    data_inspecao, inspetor, fornecedor, nr_op, familia,
                    referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas,
                    tam, def_, qtd_def or 0, hora_inicio, hora_fim, status_lote, observacao
                ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('index', sucesso=1))

@app.route('/excluir/<int:id>', methods=['GET'])
def excluir(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM checklist_qualidade WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('historico'))

@app.route('/historico', methods=['GET'])
def historico():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, data_inspecao, inspetor, fornecedor, nr_op, familia, referencia_prod, qtd_prontas, qtd_inspecionadas, tamanho, defeito, qtd_defeitos, hora_inicio, hora_fim, status_lote FROM checklist_qualidade ORDER BY id DESC;")
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
            .container { max-width: 1500px; margin: 0 auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow-x: auto; }
            h2 { color: #1e293b; margin-top: 0; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; white-space: nowrap; }
            th, td { border: 1px solid #e2e8f0; padding: 10px 12px; text-align: left; font-size: 13px; }
            th { background-color: #3b82f6; color: white; }
            tr:nth-child(even) { background-color: #f8fafc; }
            .btn-voltar { display: inline-block; padding: 10px 18px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; transition: background 0.2s; }
            .btn-voltar:hover { background: #2563eb; }
            .btn-editar { padding: 5px 10px; background: #f59e0b; color: white; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 12px; margin-right: 5px; }
            .btn-editar:hover { background: #d97706; }
            .btn-excluir { padding: 5px 10px; background: #ef4444; color: white; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 12px; }
            .btn-excluir:hover { background: #dc2626; }
            .badge-aprovado { background: #d1fae5; color: #065f46; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
            .badge-reprovado { background: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
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
                    <th>Família</th>
                    <th>Referência</th>
                    <th>Qtd Prontas</th>
                    <th>Qtd Inspecionadas</th>
                    <th>Início</th>
                    <th>Fim</th>
                    <th>Tamanho</th>
                    <th>Defeito</th>
                    <th>Qtd Defeito</th>
                    <th>Status Lote</th>
                    <th>Ações</th>
                </tr>
    '''
    for reg in registros:
        status_badge = f"<span class='badge-aprovado'>Aprovado</span>" if reg[14] == "Aprovado" else f"<span class='badge-reprovado'>Reprovado</span>" if reg[14] == "Reprovado" else reg[14]
        h_ini = reg[12] if reg[12] else ""
        h_f = reg[13] if reg[13] else ""
        html += f"<tr><td>{reg[1]}</td><td>{reg[2]}</td><td>{reg[3]}</td><td>{reg[4]}</td><td>{reg[5]}</td><td>{reg[6]}</td><td>{reg[7]}</td><td>{reg[8]}</td><td>{h_ini}</td><td>{h_f}</td><td>{reg[9]}</td><td>{reg[10]}</td><td>{reg[11]}</td><td>{status_badge}</td><td><a href='/?edit_id={reg[0]}' class='btn-editar'>✏️ Editar</a> <a href='/excluir/{reg[0]}' class='btn-excluir' onclick='return confirm(\"Tem certeza que deseja excluir este registro?\");'>🗑️ Excluir</a></td></tr>"
    
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
