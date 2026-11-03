import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Listas extraídas exatamente do arquivo XLSX
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
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    return conn

@app.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html', 
        inspetores=INSPETORES, 
        locais=LOCAIS_INSPECAO, 
        tamanhos=TAMANHOS, 
        defeitos=DEFEITOS
    )

@app.route('/salvar', methods=['POST'])
def salvar():
    data_inspecao = request.form.get('data_inspecao')
    inspetor = request.form.get('inspetor')
    fornecedor = request.form.get('fornecedor')
    nr_op = request.form.get('nr_op')
    familia = request.form.get('familia')
    referencia_prod = request.form.get('referencia_prod')
    local_inspecao = request.form.get('local_inspecao')
    qtd_prontas = request.form.get('qtd_prontas') or 0
    qtd_inspecionadas = request.form.get('qtd_inspecionadas') or 0
    tamanho = request.form.get('tamanho')
    defeito = request.form.get('defeito')
    qtd_defeitos = request.form.get('qtd_defeitos') or 0
    observacao = request.form.get('observacao')

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Cria a tabela no PostgreSQL caso ainda não exista
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

    # Insere o registro de inspeção
    cur.execute('''
        INSERT INTO checklist_qualidade (
            data_inspecao, inspetor, fornecedor, nr_op, familia, 
            referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas, 
            tamanho, defeito, qtd_defeitos, observacao
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        data_inspecao, inspetor, fornecedor, nr_op, familia,
        referencia_prod, local_inspecao, qtd_prontas, qtd_inspecionadas,
        tamanho, defeito, qtd_defeitos, observacao
    ))
    
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)