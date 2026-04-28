import os
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from models import db, Vendedor, Comissao
from src.report import Report
import pandas as pd
import io
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() # Garante que saia no terminal
    ]
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ssw-dashboard-secret' # Simples para uso local

db.init_app(app)

# Cria as tabelas se não existirem
with app.app_context():
    db.create_all()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Se havia um session_id antigo que não foi deslogado, limpar os dados dele!
        old_session_id = session.get('session_id')
        if old_session_id:
            try:
                Comissao.query.filter_by(session_id=old_session_id).delete()
                Vendedor.query.filter_by(session_id=old_session_id).delete()
                db.session.commit()
            except:
                db.session.rollback()
                
        session['company'] = 'rcs'
        session['tax'] = request.form.get('tax')
        session['user'] = request.form.get('user')
        session['password'] = request.form.get('password')
        session['session_id'] = str(uuid.uuid4())
        
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session_id = session.get('session_id')
    if session_id:
        try:
            Comissao.query.filter_by(session_id=session_id).delete()
            Vendedor.query.filter_by(session_id=session_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
            
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session or 'session_id' not in session:
        return redirect(url_for('login'))
        
    s_id = session['session_id']
    vendedores = Vendedor.query.filter_by(session_id=s_id).order_by(Vendedor.equipe.asc(), Vendedor.codigo.asc()).all()
    total = len(vendedores)
    sucesso = Vendedor.query.filter_by(session_id=s_id, status='Sucesso').count()
    vazio = Vendedor.query.filter_by(session_id=s_id).filter(Vendedor.status.in_(['Vazio', 'Sem Dados'])).count()
    erro = Vendedor.query.filter_by(session_id=s_id, status='Erro').count()
    
    stats = {
        "total": total,
        "sucesso": sucesso,
        "vazio": vazio,
        "erro": erro
    }
    return render_template('index.html', vendedores=vendedores, stats=stats)

@app.route('/import', methods=['POST'])
def import_vendedores():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        # Mapeamento de colunas (conforme solicitado pelo usuário)
        # Equipe, Código, Vendedor, Filial, Nome
        required_cols = ['Equipe', 'Código', 'Vendedor', 'Filial', 'Nome']
        for col in required_cols:
            if col not in df.columns:
                return f"Coluna obrigatória ausente: {col}", 400
        
        for _, row in df.iterrows():
            codigo = str(row['Código'])
            vendedor = Vendedor.query.filter_by(session_id=session['session_id'], codigo=codigo).first()
            if not vendedor:
                vendedor = Vendedor(session_id=session['session_id'], codigo=codigo)
            
            vendedor.equipe = row['Equipe']
            vendedor.vendedor_nome = row['Vendedor']
            vendedor.filial = row['Filial']
            vendedor.nome_completo = row['Nome']
            vendedor.status = 'Pendente'
            db.session.add(vendedor)
            
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        return f"Erro na importação: {str(e)}", 500

@app.route('/template')
def download_template():
    # Cria um modelo Excel vazio com as colunas corretas
    cols = ['Equipe', 'Código', 'Vendedor', 'Filial', 'Nome']
    df = pd.DataFrame(columns=cols)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Modelo')
    output.seek(0)
    return send_file(output, download_name="modelo_importacao.xlsx", as_attachment=True)

@app.route('/export/vendedores')
def export_vendedores():
    if 'session_id' not in session: return redirect(url_for('login'))
    vendedores = Vendedor.query.filter_by(session_id=session['session_id']).all()
    data = []
    for v in vendedores:
        data.append({
            'Equipe': v.equipe,
            'Código': v.codigo,
            'Vendedor': v.vendedor_nome,
            'Filial': v.filial,
            'Nome': v.nome_completo,
            'Status': v.status,
            'Última Consulta': v.ultima_consulta
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="vendedores.xlsx", as_attachment=True)

@app.route('/export/comissoes')
def export_comissoes():
    if 'session_id' not in session: return redirect(url_for('login'))
    comissoes = Comissao.query.filter_by(session_id=session['session_id']).order_by(Comissao.timestamp.desc()).all()
    data = []
    for c in comissoes:
        data.append({
            'Equipe': c.equipe,
            'Código': c.codigo,
            'Vendedor': c.vendedor,
            'Filial': c.filial,
            'Nome': c.nome_vendedor,
            'Clientes': c.clientes,
            'CNPJ': c.cnpj,
            'Cidade': c.cidade,
            'Nome_Cliente': c.nome_cliente,
            'Conquista_Inicio': c.conquista_inicio,
            'Conquista_Fim': c.conquista_fim,
            'Conquista_Pct': c.conquista_pct,
            'Manut_1_Inicio': c.manut_1_inicio,
            'Manut_1_Fim': c.manut_1_fim,
            'Manut_1_Pct': c.manut_1_pct,
            'Manut_2_Inicio': c.manut_2_inicio,
            'Manut_2_Fim': c.manut_2_fim,
            'Manut_2_Pct': c.manut_2_pct,
            'Mercadoria': c.mercadoria,
            'Observação': c.observacao,
            'Consulta_ID': c.consulta_id,
            'Data_Registro': c.timestamp
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="comissoes.xlsx", as_attachment=True)

@app.route('/consultar', methods=['POST'])
def consultar():
    if 'user' not in session or 'session_id' not in session:
        return jsonify({"status": "Erro", "msg": "Usuário não autenticado"}), 401
    
    user = {
        'company': session['company'], 
        'tax': session['tax'], 
        'user': session['user'], 
        'password': session['password']
    }
    
    report = Report(user, 'https://sistema.ssw.inf.br/bin/ssw0014')
    codigos = request.json.get('codigos', [])
    s_id = session['session_id']
    def stream():
        with app.app_context():
            for res in report.run(s_id, codigos):
                yield json.dumps(res) + "\n"

    return app.response_class(stream(), mimetype='application/x-ndjson')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
