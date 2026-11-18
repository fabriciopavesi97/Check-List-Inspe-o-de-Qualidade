import csv
import io
import os
from datetime import datetime, time
import psycopg2
from flask import Flask, Response, redirect, render_template, request, url_for

app = Flask(__name__)

INSPETORES_PADRAO = ["Inspetor 1", "Inspetor 2", "Inspetor 3", "Inspetor 4"]
LOCAIS_INSPECAO = ["Externa", "Ibirama", "Brusque"]
TIPOS_INSPECAO = ["1ª Inspeção", "Reinspeção"]

FORNECEDORES_PADRAO = [
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

DEFEITOS_PADRAO = [
    "Nenhum Defeito Encontrado (Lote Perfeito)",
    "Alça Torcida",
    "Arremate com bolinha",
    "Arremate desencontrado",
    "Bainha com bananinha",
    "Bainha cortada",
    "Bainha desencontrada",
    "Bainha torcida/enviasada",
    "Barramento",
    "Biquinho decote com acabamento mal feito",
    "Biquinho decote fora do centro",
    "Bolsos Tortos",
    "Casamento de recortes",
    "Composição errada",
    "Contaminação / fibras estranhas",
    "Cós escapado",
    "Costura enrrugada",
    "Costura escapada",
    "Costura estourada",
    "Costura torta",
    "Decote esgaçado",
    "Decote franzido",
    "Desencaixe de estampa",
    "Diferença de cavas",
    "Emenda Materia prima",
    "Emenda na costura",
    "Estampa falhada",
    "Etiqueta de tamanho trocada",
    "Etiqueta errada",
    "Etiqueta lado errado",
    "Etiqueta torta",
    "Falso amarrador mal costurado",
    "Falso amarrador no lugar errado",
    "Falta travete",
    "Furo de agulha (na peça e etiqueta)",
    "Furo de malha",
    "Lacinho mal pregado",
    "Linha do Franzido aparecendo",
    "Manchas",
    "Marca de costura desmanchada",
    "Marcação do final do rolo",
    "Medidas (fora tolerância)",
    "Óleo de costura",
    "Óleo de Tinturaria",
    "Peça cortada",
    "Peça molhada",
    "Peça sem etiqueta",
    "Peça sem lacinho",
    "Peitilho torto",
    "Ponto falhado",
    "Prega na costura",
    "Rebarba de bainha",
    "Regulagem de ponto",
    "Sobra de fios Costura",
    "Sujeiras",
    "Tonalidade",
    "Torção",
    "Transfer com tamanho errado",
    "Transfer descolando",
    "Transfer falhado",
    "Transfer fora do centro",
    "Viés caído",
    "Viés escapado",
    "Vinco"
]


def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)


def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Tabelas de catálogo centralizadas no banco
        cur.execute('''
            CREATE TABLE IF NOT EXISTS catalogo_fornecedores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(150) UNIQUE NOT NULL,
                ativo BOOLEAN DEFAULT TRUE
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS catalogo_inspetores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) UNIQUE NOT NULL,
                ativo BOOLEAN DEFAULT TRUE
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS catalogo_defeitos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(150) UNIQUE NOT NULL,
                ordem_fixa INT DEFAULT 999,
                ativo BOOLEAN DEFAULT TRUE
            );
        ''')

        # Tabela principal de inspeções
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
                tipo_inspecao VARCHAR(30) DEFAULT '1ª Inspeção',
                qtd_prontas INT,
                qtd_inspecionadas INT,
                tamanho VARCHAR(20),
                defeito VARCHAR(150),
                qtd_defeitos INT,
                hora_inicio TIME,
                hora_fim TIME,
                status_lote VARCHAR(20),
                observacao TEXT,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP
            );
        ''')

        # Garante colunas novas caso a tabela já exista
        cur.execute("ALTER TABLE checklist_qualidade ADD COLUMN IF NOT EXISTS tipo_inspecao VARCHAR(30) DEFAULT '1ª Inspeção';")
        cur.execute("ALTER TABLE checklist_qualidade ADD COLUMN IF NOT EXISTS hora_inicio TIME;")
        cur.execute("ALTER TABLE checklist_qualidade ADD COLUMN IF NOT EXISTS hora_fim TIME;")
        cur.execute("ALTER TABLE checklist_qualidade ADD COLUMN IF NOT EXISTS status_lote VARCHAR(20);")
        cur.execute("ALTER TABLE checklist_qualidade ADD COLUMN IF NOT EXISTS data_atualizacao TIMESTAMP;")

        # Tabela de log de alterações e exclusões
        cur.execute('''
            CREATE TABLE IF NOT EXISTS log_auditoria_checklist (
                id SERIAL PRIMARY KEY,
                registro_id INT,
                acao VARCHAR(20) NOT NULL,
                nr_op VARCHAR(50),
                fornecedor VARCHAR(150),
                inspetor VARCHAR(100),
                detalhes TEXT,
                data_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Popula catálogos caso estejam vazios
        for f in FORNECEDORES_PADRAO:
            cur.execute(
                "INSERT INTO catalogo_fornecedores (nome, ativo) VALUES (%s, TRUE) ON CONFLICT (nome) DO NOTHING;",
                (f,)
            )

        for insp in INSPETORES_PADRAO:
            cur.execute(
                "INSERT INTO catalogo_inspetores (nome, ativo) VALUES (%s, TRUE) ON CONFLICT (nome) DO NOTHING;",
                (insp,)
            )

        for idx, d in enumerate(DEFEITOS_PADRAO):
            ordem = 0 if idx == 0 else 100
            cur.execute(
                "INSERT INTO catalogo_defeitos (nome, ordem_fixa, ativo) VALUES (%s, %s, TRUE) ON CONFLICT (nome) DO NOTHING;",
                (d, ordem)
            )

        # View pronta para o Power BI com colunas calculadas
        cur.execute("DROP VIEW IF EXISTS vw_checklist_qualidade_bi;")
        cur.execute('''
            CREATE VIEW vw_checklist_qualidade_bi AS
            SELECT
                id,
                data_inspecao,
                TO_CHAR(data_inspecao, 'YYYY-MM') AS mes_ano,
                CONCAT(COALESCE(nr_op, ''), '_', COALESCE(TO_CHAR(data_inspecao, 'YYYY-MM-DD'), '')) AS chave_lote,
                inspetor,
                fornecedor,
                nr_op,
                familia,
                referencia_prod,
                local_inspecao,
                COALESCE(tipo_inspecao, '1ª Inspeção') AS tipo_inspecao,
                qtd_prontas,
                qtd_inspecionadas,
                tamanho,
                defeito,
                qtd_defeitos,
                hora_inicio,
                hora_fim,
                CASE
                    WHEN hora_inicio IS NOT NULL AND hora_fim IS NOT NULL THEN
                        CASE
                            WHEN (EXTRACT(HOUR FROM hora_fim) * 60 + EXTRACT(MINUTE FROM hora_fim)) >=
                                 (EXTRACT(HOUR FROM hora_inicio) * 60 + EXTRACT(MINUTE FROM hora_inicio))
                            THEN ((EXTRACT(HOUR FROM hora_fim) * 60 + EXTRACT(MINUTE FROM hora_fim)) -
                                  (EXTRACT(HOUR FROM hora_inicio) * 60 + EXTRACT(MINUTE FROM hora_inicio)))::INT
                            ELSE (((EXTRACT(HOUR FROM hora_fim) * 60 + EXTRACT(MINUTE FROM hora_fim)) + 1440) -
                                  (EXTRACT(HOUR FROM hora_inicio) * 60 + EXTRACT(MINUTE FROM hora_inicio)))::INT
                        END
                    ELSE NULL
                END AS duracao_min,
                status_lote,
                observacao,
                data_registro,
                data_atualizacao
            FROM checklist_qualidade;
        ''')

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar/atualizar tabela, catálogos ou view: {e}")


init_db()


def obter_catalogos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT nome FROM catalogo_fornecedores WHERE ativo = TRUE ORDER BY id ASC;")
        fornecedores = [row[0] for row in cur.fetchall()] or FORNECEDORES_PADRAO

        cur.execute("SELECT nome FROM catalogo_inspetores WHERE ativo = TRUE ORDER BY id ASC;")
        inspetores = [row[0] for row in cur.fetchall()] or INSPETORES_PADRAO

        cur.execute(
            "SELECT nome FROM catalogo_defeitos WHERE ativo = TRUE "
            "ORDER BY ordem_fixa ASC, nome ASC;"
        )
        defeitos = [row[0] for row in cur.fetchall()] or DEFEITOS_PADRAO

        cur.close()
        conn.close()
        return fornecedores, inspetores, defeitos
    except Exception:
        return FORNECEDORES_PADRAO, INSPETORES_PADRAO, DEFEITOS_PADRAO


def registrar_log(cur, registro_id, acao, nr_op, fornecedor, inspetor, detalhes):
    cur.execute(
        '''
        INSERT INTO log_auditoria_checklist
            (registro_id, acao, nr_op, fornecedor, inspetor, detalhes)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''',
        (registro_id, acao, nr_op, fornecedor, inspetor, detalhes)
    )


def calcular_campos_derivados(data_inspecao, nr_op, hora_inicio, hora_fim):
    data_str = ""
    mes_ano = ""
    if data_inspecao:
        if isinstance(data_inspecao, str):
            dt_obj = datetime.strptime(data_inspecao[:10], '%Y-%m-%d')
        else:
            dt_obj = data_inspecao
        data_str = dt_obj.strftime('%Y-%m-%d')
        mes_ano = dt_obj.strftime('%Y-%m')

    chave_lote = f"{nr_op or ''}_{data_str}".strip("_")

    duracao_min = ""
    if hora_inicio and hora_fim:
        if isinstance(hora_inicio, time):
            min_ini = hora_inicio.hour * 60 + hora_inicio.minute
        else:
            h, m = map(int, str(hora_inicio).split(':')[:2])
            min_ini = h * 60 + m

        if isinstance(hora_fim, time):
            min_fim = hora_fim.hour * 60 + hora_fim.minute
        else:
            h, m = map(int, str(hora_fim).split(':')[:2])
            min_fim = h * 60 + m

        diff = min_fim - min_ini
        if diff < 0:
            diff += 24 * 60
        duracao_min = diff

    return chave_lote, mes_ano, duracao_min


def validar_quantidades(qtd_prontas, qtd_inspecionadas, lista_defeitos, qtds_defeitos, is_edicao=False):
    if qtd_inspecionadas > qtd_prontas:
        return (
            f"A quantidade inspecionada ({qtd_inspecionadas}) não pode ser maior que "
            f"a quantidade de peças prontas ({qtd_prontas})."
        )

    if is_edicao:
        qtd_def_edit = qtds_defeitos[0] if qtds_defeitos else 0
        if qtd_def_edit > qtd_inspecionadas:
            return (
                f"A quantidade de peças com defeito ({qtd_def_edit}) não pode ser maior que "
                f"a quantidade de peças inspecionadas ({qtd_inspecionadas})."
            )
        return None

    soma_defeitos = 0
    for def_, qtd_def in zip(lista_defeitos, qtds_defeitos):
        if def_:
            soma_defeitos += (qtd_def or 0)

    if soma_defeitos > qtd_inspecionadas:
        return (
            f"A soma das peças com defeito ({soma_defeitos}) não pode ser maior que "
            f"a quantidade de peças inspecionadas ({qtd_inspecionadas})."
        )

    return None


@app.route('/', methods=['GET'])
def index():
    sucesso = request.args.get('sucesso')
    edit_id = request.args.get('edit_id')
    registro = None
    fornecedores, inspetores, defeitos = obter_catalogos()

    if edit_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, data_inspecao, inspetor, fornecedor, nr_op, familia, referencia_prod, "
            "local_inspecao, COALESCE(tipo_inspecao, '1ª Inspeção'), qtd_prontas, qtd_inspecionadas, "
            "tamanho, defeito, qtd_defeitos, hora_inicio, hora_fim, status_lote, observacao "
            "FROM checklist_qualidade WHERE id = %s;",
            (edit_id,)
        )
        registro = cur.fetchone()
        cur.close()
        conn.close()

    return render_template(
        'index.html',
        inspetores=inspetores,
        locais=LOCAIS_INSPECAO,
        tipos_inspecao=TIPOS_INSPECAO,
        fornecedores=fornecedores,
        tamanhos=TAMANHOS,
        defeitos=defeitos,
        sucesso=sucesso,
        registro=registro,
        erro=None
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
    tipo_inspecao = request.form.get('tipo_inspecao') or '1ª Inspeção'
    qtd_prontas = int(request.form.get('qtd_prontas') or 0)
    qtd_inspecionadas = int(request.form.get('qtd_inspecionadas') or 0)
    hora_inicio = request.form.get('hora_inicio') or None
    hora_fim = request.form.get('hora_fim') or None
    status_lote = request.form.get('status_lote')
    observacao = request.form.get('observacao')

    tamanhos = request.form.getlist('tamanho[]')
    lista_defeitos = request.form.getlist('defeito[]')
    qtds_defeitos = [int(q or 0) for q in request.form.getlist('qtd_defeitos[]')]

    fornecedores, inspetores, defeitos = obter_catalogos()
    is_edicao = bool(registro_id)

    erro = validar_quantidades(
        qtd_prontas, qtd_inspecionadas, lista_defeitos, qtds_defeitos, is_edicao=is_edicao
    )
    if erro:
        registro = None
        if is_edicao:
            registro = (
                registro_id, data_inspecao, inspetor, fornecedor, nr_op, familia,
                referencia_prod, local_inspecao, tipo_inspecao, qtd_prontas, qtd_inspecionadas,
                tamanhos[0] if tamanhos else '',
                lista_defeitos[0] if lista_defeitos else '',
                qtds_defeitos[0] if qtds_defeitos else 0,
                hora_inicio, hora_fim, status_lote, observacao
            )
        return render_template(
            'index.html',
            inspetores=inspetores,
            locais=LOCAIS_INSPECAO,
            tipos_inspecao=TIPOS_INSPECAO,
            fornecedores=fornecedores,
            tamanhos=TAMANHOS,
            defeitos=defeitos,
            sucesso=None,
            registro=registro,
            erro=erro
        )

    conn = get_db_connection()
    cur = conn.cursor()

    if is_edicao:
        if len(tamanhos) > 0 and lista_defeitos[0]:
            cur.execute(
                "SELECT defeito, qtd_defeitos, status_lote FROM checklist_qualidade WHERE id = %s;",
                (registro_id,)
            )
            anterior = cur.fetchone()

            cur.execute('''
                UPDATE checklist_qualidade SET
                    data_inspecao = %s, inspetor = %s, fornecedor = %s, nr_op = %s,
                    familia = %s, referencia_prod = %s, local_inspecao = %s,
                    tipo_inspecao = %s, qtd_prontas = %s, qtd_inspecionadas = %s,
                    tamanho = %s, defeito = %s, qtd_defeitos = %s,
                    hora_inicio = %s, hora_fim = %s, status_lote = %s,
                    observacao = %s, data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (
                data_inspecao, inspetor, fornecedor, nr_op, familia,
                referencia_prod, local_inspecao, tipo_inspecao, qtd_prontas, qtd_inspecionadas,
                tamanhos[0], lista_defeitos[0], qtds_defeitos[0],
                hora_inicio, hora_fim, status_lote, observacao, registro_id
            ))

            detalhes_log = (
                f"Registro #{registro_id} editado ({tipo_inspecao}, Status: {status_lote}, "
                f"Defeito: {lista_defeitos[0]} [{qtds_defeitos[0]}])."
            )
            if anterior:
                detalhes_log += f" Anterior -> Defeito: {anterior[0]} [{anterior[1]}], Status: {anterior[2]}."

            registrar_log(
                cur, int(registro_id), "EDITAR", nr_op, fornecedor, inspetor, detalhes_log
            )
    else:
        for tam, def_, qtd_def in zip(tamanhos, lista_defeitos, qtds_defeitos):
            if def_:
                cur.execute('''
                    INSERT INTO checklist_qualidade (
                        data_inspecao, inspetor, fornecedor, nr_op, familia,
                        referencia_prod, local_inspecao, tipo_inspecao, qtd_prontas,
                        qtd_inspecionadas, tamanho, defeito, qtd_defeitos,
                        hora_inicio, hora_fim, status_lote, observacao
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    data_inspecao, inspetor, fornecedor, nr_op, familia,
                    referencia_prod, local_inspecao, tipo_inspecao, qtd_prontas,
                    qtd_inspecionadas, tam, def_, qtd_def,
                    hora_inicio, hora_fim, status_lote, observacao
                ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('index', sucesso=1))


@app.route('/excluir/<int:id>', methods=['GET'])
def excluir(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT nr_op, fornecedor, inspetor, defeito, qtd_defeitos, status_lote "
        "FROM checklist_qualidade WHERE id = %s;",
        (id,)
    )
    dados = cur.fetchone()

    cur.execute("DELETE FROM checklist_qualidade WHERE id = %s;", (id,))

    if dados:
        detalhes = (
            f"Registro #{id} excluído (Defeito: {dados[3]} [{dados[4]}], Status: {dados[5]})."
        )
        registrar_log(cur, id, "EXCLUIR", dados[0], dados[1], dados[2], detalhes)

    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('historico'))


def buscar_registros_filtrados():
    filtro_op = request.args.get('op', '').strip()
    filtro_fornecedor = request.args.get('fornecedor', '').strip()
    filtro_inspetor = request.args.get('inspetor', '').strip()
    filtro_status = request.args.get('status', '').strip()
    filtro_tipo = request.args.get('tipo', '').strip()
    filtro_data_ini = request.args.get('data_ini', '').strip()
    filtro_data_fim = request.args.get('data_fim', '').strip()

    query = (
        "SELECT id, data_inspecao, inspetor, fornecedor, nr_op, familia, referencia_prod, "
        "qtd_prontas, qtd_inspecionadas, tamanho, defeito, qtd_defeitos, hora_inicio, hora_fim, "
        "status_lote, COALESCE(tipo_inspecao, '1ª Inspeção'), data_atualizacao "
        "FROM checklist_qualidade WHERE 1=1"
    )
    params = []

    if filtro_op:
        query += " AND nr_op ILIKE %s"
        params.append(f"%{filtro_op}%")
    if filtro_fornecedor:
        query += " AND fornecedor = %s"
        params.append(filtro_fornecedor)
    if filtro_inspetor:
        query += " AND inspetor = %s"
        params.append(filtro_inspetor)
    if filtro_status:
        query += " AND status_lote = %s"
        params.append(filtro_status)
    if filtro_tipo:
        query += " AND COALESCE(tipo_inspecao, '1ª Inspeção') = %s"
        params.append(filtro_tipo)
    if filtro_data_ini:
        query += " AND data_inspecao >= %s"
        params.append(filtro_data_ini)
    if filtro_data_fim:
        query += " AND data_inspecao <= %s"
        params.append(filtro_data_fim)

    query += " ORDER BY id DESC;"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    registros = cur.fetchall()
    cur.close()
    conn.close()

    filtros = {
        'op': filtro_op,
        'fornecedor': filtro_fornecedor,
        'inspetor': filtro_inspetor,
        'status': filtro_status,
        'tipo': filtro_tipo,
        'data_ini': filtro_data_ini,
        'data_fim': filtro_data_fim,
    }
    return registros, filtros


@app.route('/historico/exportar', methods=['GET'])
def exportar_historico():
    registros, _ = buscar_registros_filtrados()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow([
        "Data", "Mês/Ano", "Chave Lote", "Tipo Inspeção", "Inspetor", "Fornecedor",
        "N° OP", "Família", "Referência", "Qtd Prontas", "Qtd Inspecionadas",
        "Início", "Fim", "Duração (min)", "Tamanho", "Defeito",
        "Qtd Defeito", "Status Lote", "Última Alteração"
    ])

    for reg in registros:
        chave_lote, mes_ano, duracao_min = calcular_campos_derivados(reg[1], reg[4], reg[12], reg[13])
        dt_alt = reg[16].strftime('%Y-%m-%d %H:%M') if reg[16] else ""
        writer.writerow([
            reg[1], mes_ano, chave_lote, reg[15], reg[2], reg[3], reg[4],
            reg[5], reg[6], reg[7], reg[8], reg[12] or "", reg[13] or "",
            duracao_min, reg[9], reg[10], reg[11], reg[14] or "", dt_alt
        ])

    csv_bytes = ("\ufeff" + output.getvalue()).encode('utf-8')
    return Response(
        csv_bytes,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=historico_inspecoes.csv"}
    )


@app.route('/historico', methods=['GET'])
def historico():
    registros_filtrados, filtros = buscar_registros_filtrados()
    fornecedores, inspetores, _ = obter_catalogos()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT data_inspecao, fornecedor, nr_op, defeito, qtd_defeitos, status_lote "
        "FROM checklist_qualidade;"
    )
    todos_mes = cur.fetchall()

    cur.execute(
        "SELECT registro_id, acao, nr_op, fornecedor, inspetor, detalhes, "
        "TO_CHAR(data_evento, 'YYYY-MM-DD HH24:MI') "
        "FROM log_auditoria_checklist ORDER BY id DESC LIMIT 20;"
    )
    logs = cur.fetchall()
    cur.close()
    conn.close()

    mes_atual = datetime.now().month
    ano_atual = datetime.now().year

    total_lotes_mes = set()
    lotes_reprovados_mes = set()
    faccoes_reprovadas = {}
    defeitos_recorrentes = {}

    for data_insp, fornecedor, op, defeito, q_def, status in todos_mes:
        if data_insp:
            dt_obj = datetime.strptime(data_insp, '%Y-%m-%d') if isinstance(data_insp, str) else data_insp
            if dt_obj.month == mes_atual and dt_obj.year == ano_atual:
                total_lotes_mes.add(f"{op}_{dt_obj.strftime('%Y-%m-%d')}")
                if status == "Reprovado":
                    lotes_reprovados_mes.add(f"{op}_{dt_obj.strftime('%Y-%m-%d')}")
                    faccoes_reprovadas[fornecedor] = faccoes_reprovadas.get(fornecedor, 0) + 1
                if defeito and "Nenhum Defeito" not in defeito:
                    defeitos_recorrentes[defeito] = defeitos_recorrentes.get(defeito, 0) + (q_def or 1)

    qtd_lotes_mes_count = len(total_lotes_mes)
    qtd_reprovados_mes_count = len(lotes_reprovados_mes)
    indice_reprovados_mes = (qtd_reprovados_mes_count / qtd_lotes_mes_count * 100) if qtd_lotes_mes_count > 0 else 0

    ranking_faccoes = sorted(faccoes_reprovadas.items(), key=lambda x: x[1], reverse=True)[:5]
    ranking_defeitos = sorted(defeitos_recorrentes.items(), key=lambda x: x[1], reverse=True)[:5]

    opcoes_fornecedor = '<option value="">Todos os fornecedores</option>'
    for f in fornecedores:
        sel = 'selected' if filtros['fornecedor'] == f else ''
        opcoes_fornecedor += f'<option value="{f}" {sel}>{f}</option>'

    opcoes_inspetor = '<option value="">Todos os inspetores</option>'
    for insp in inspetores:
        sel = 'selected' if filtros['inspetor'] == insp else ''
        opcoes_inspetor += f'<option value="{insp}" {sel}>{insp}</option>'

    opcoes_status = (
        '<option value="">Todos os status</option>'
        f'<option value="Aprovado" {"selected" if filtros["status"] == "Aprovado" else ""}>Aprovado</option>'
        f'<option value="Reprovado" {"selected" if filtros["status"] == "Reprovado" else ""}>Reprovado</option>'
    )

    opcoes_tipo = (
        '<option value="">Todos os tipos</option>'
        f'<option value="1ª Inspeção" {"selected" if filtros["tipo"] == "1ª Inspeção" else ""}>1ª Inspeção</option>'
        f'<option value="Reinspeção" {"selected" if filtros["tipo"] == "Reinspeção" else ""}>Reinspeção</option>'
    )

    qs = request.query_string.decode('utf-8')
    url_exportar = f"/historico/exportar?{qs}" if qs else "/historico/exportar"

    html = f'''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Histórico e Indicadores de Qualidade</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 30px; background: #f0f2f5; color: #333; }}
            .container {{ max-width: 1700px; margin: 0 auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow-x: auto; }}
            h2 {{ color: #1e293b; margin-top: 0; }}
            .top-actions {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}

            .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin: 20px 0 25px 0; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
            .card h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #64748b; text-transform: uppercase; }}
            .card .value {{ font-size: 24px; font-weight: 700; color: #1e293b; }}
            .card ul {{ margin: 5px 0 0 0; padding-left: 15px; font-size: 13px; color: #334155; }}
            .card li {{ margin-bottom: 4px; }}

            .filtros-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 20px; }}
            .filtros-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; align-items: end; }}
            .filtros-box label {{ display: block; font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 4px; }}
            .filtros-box input, .filtros-box select {{ width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 13px; background: white; }}
            .filtros-btns {{ display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }}

            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; white-space: nowrap; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 10px 12px; text-align: left; font-size: 13px; }}
            th {{ background-color: #3b82f6; color: white; }}
            tr:nth-child(even) {{ background-color: #f8fafc; }}
            .btn-voltar {{ display: inline-block; padding: 10px 18px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; }}
            .btn-voltar:hover {{ background: #2563eb; }}
            .btn-exportar {{ display: inline-block; padding: 10px 18px; background: #10b981; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; }}
            .btn-exportar:hover {{ background: #059669; }}
            .btn-filtrar {{ padding: 8px 14px; background: #1e293b; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; }}
            .btn-limpar {{ padding: 8px 14px; background: #e2e8f0; color: #334155; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 13px; }}
            .btn-editar {{ padding: 5px 10px; background: #f59e0b; color: white; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 12px; margin-right: 5px; }}
            .btn-excluir {{ padding: 5px 10px; background: #ef4444; color: white; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 12px; }}
            .badge-aprovado {{ background: #d1fae5; color: #065f46; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }}
            .badge-reprovado {{ background: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }}
            .badge-tipo {{ background: #e0f2fe; color: #0369a1; padding: 3px 7px; border-radius: 4px; font-weight: 600; font-size: 11px; }}
            .log-box {{ margin-top: 35px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📊 Painel de Indicadores & Histórico de Inspeções</h2>
            <p style="color: #64748b; font-size: 14px;">Resumo do mês atual, campos calculados, controle de reinspeção e log de auditoria.</p>
            <div class="top-actions">
                <a href="/" class="btn-voltar">← Voltar para o Formulário</a>
                <a href="{url_exportar}" class="btn-exportar">📥 Exportar CSV (Excel)</a>
            </div>

            <div class="cards-grid">
                <div class="card">
                    <h3>Lotes Inspecionados (Mês)</h3>
                    <div class="value">{qtd_lotes_mes_count}</div>
                </div>
                <div class="card">
                    <h3>Índice de Reprovados (Mês)</h3>
                    <div class="value" style="color: {'#dc2626' if indice_reprovados_mes > 0 else '#059669'};">{indice_reprovados_mes:.1f}%</div>
                </div>
                <div class="card">
                    <h3>Top Facções Reprovadas</h3>
                    <ul>
    '''

    if ranking_faccoes:
        for faccao, qtd in ranking_faccoes:
            html += f"<li><b>{faccao}</b>: {qtd} lote(s)</li>"
    else:
        html += "<li>Nenhuma reprovação no mês.</li>"

    html += '''
                    </ul>
                </div>
                <div class="card">
                    <h3>Defeitos Mais Recorrentes</h3>
                    <ul>
    '''

    if ranking_defeitos:
        for defeito, qtd in ranking_defeitos:
            html += f"<li><b>{defeito}</b>: {qtd} ocorrência(s)</li>"
    else:
        html += "<li>Nenhum defeito registrado.</li>"

    html += f'''
                    </ul>
                </div>
            </div>

            <form method="GET" action="/historico" class="filtros-box">
                <div class="filtros-grid">
                    <div>
                        <label for="op">N° OP</label>
                        <input type="text" id="op" name="op" value="{filtros['op']}" placeholder="Ex: 10452">
                    </div>
                    <div>
                        <label for="fornecedor">Fornecedor</label>
                        <select id="fornecedor" name="fornecedor">{opcoes_fornecedor}</select>
                    </div>
                    <div>
                        <label for="inspetor">Inspetor</label>
                        <select id="inspetor" name="inspetor">{opcoes_inspetor}</select>
                    </div>
                    <div>
                        <label for="tipo">Tipo Inspeção</label>
                        <select id="tipo" name="tipo">{opcoes_tipo}</select>
                    </div>
                    <div>
                        <label for="status">Status</label>
                        <select id="status" name="status">{opcoes_status}</select>
                    </div>
                    <div>
                        <label for="data_ini">Data De</label>
                        <input type="date" id="data_ini" name="data_ini" value="{filtros['data_ini']}">
                    </div>
                    <div>
                        <label for="data_fim">Data Até</label>
                        <input type="date" id="data_fim" name="data_fim" value="{filtros['data_fim']}">
                    </div>
                </div>
                <div class="filtros-btns">
                    <button type="submit" class="btn-filtrar">🔍 Aplicar Filtros</button>
                    <a href="/historico" class="btn-limpar">Limpar Filtros</a>
                </div>
            </form>

            <h3 style="color: #1e293b; margin-top: 10px;">Histórico Detalhado ({len(registros_filtrados)} linha(s))</h3>
            <table>
                <tr>
                    <th>Data</th>
                    <th>Mês/Ano</th>
                    <th>Chave Lote</th>
                    <th>Tipo</th>
                    <th>Inspetor</th>
                    <th>Fornecedor</th>
                    <th>N° OP</th>
                    <th>Família</th>
                    <th>Referência</th>
                    <th>Qtd Prontas</th>
                    <th>Qtd Inspecionadas</th>
                    <th>Início</th>
                    <th>Fim</th>
                    <th>Duração (min)</th>
                    <th>Tamanho</th>
                    <th>Defeito</th>
                    <th>Qtd Defeito</th>
                    <th>Status Lote</th>
                    <th>Alterado em</th>
                    <th>Ações</th>
                </tr>
    '''

    for reg in registros_filtrados:
        chave_lote, mes_ano, duracao_min = calcular_campos_derivados(reg[1], reg[4], reg[12], reg[13])
        status_badge = (
            "<span class='badge-aprovado'>Aprovado</span>" if reg[14] == "Aprovado"
            else "<span class='badge-reprovado'>Reprovado</span>" if reg[14] == "Reprovado"
            else (reg[14] or "")
        )
        tipo_badge = f"<span class='badge-tipo'>{reg[15]}</span>"
        h_ini = reg[12] if reg[12] else ""
        h_f = reg[13] if reg[13] else ""
        dur_txt = f"{duracao_min} min" if duracao_min != "" else ""
        dt_alt = reg[16].strftime('%d/%m/%Y %H:%M') if reg[16] else "-"
        html += (
            f"<tr><td>{reg[1]}</td><td>{mes_ano}</td><td>{chave_lote}</td><td>{tipo_badge}</td>"
            f"<td>{reg[2]}</td><td>{reg[3]}</td><td>{reg[4]}</td><td>{reg[5]}</td>"
            f"<td>{reg[6]}</td><td>{reg[7]}</td><td>{reg[8]}</td><td>{h_ini}</td>"
            f"<td>{h_f}</td><td>{dur_txt}</td><td>{reg[9]}</td><td>{reg[10]}</td>"
            f"<td>{reg[11]}</td><td>{status_badge}</td><td>{dt_alt}</td>"
            f"<td><a href='/?edit_id={reg[0]}' class='btn-editar'>✏️ Editar</a> "
            f"<a href='/excluir/{reg[0]}' class='btn-excluir' "
            f"onclick='return confirm(\"Tem certeza que deseja excluir este registro?\");'>🗑️ Excluir</a></td></tr>"
        )

    html += '''
            </table>

            <div class="log-box">
                <h3 style="color: #1e293b; margin-top: 0;">🛡️ Log de Auditoria (Últimas Edições e Exclusões)</h3>
                <table>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Ação</th>
                        <th>ID</th>
                        <th>N° OP</th>
                        <th>Fornecedor</th>
                        <th>Inspetor</th>
                        <th>Detalhes</th>
                    </tr>
    '''

    if logs:
        for l in logs:
            html += (
                f"<tr><td>{l[6]}</td><td><b>{l[1]}</b></td><td>{l[0]}</td>"
                f"<td>{l[2] or '-'}</td><td>{l[3] or '-'}</td><td>{l[4] or '-'}</td><td>{l[5]}</td></tr>"
            )
    else:
        html += "<tr><td colspan='7'>Nenhuma edição ou exclusão registrada até o momento.</td></tr>"

    html += '''
                </table>
            </div>
        </div>
    </body>
    </html>
    '''
    return html


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
