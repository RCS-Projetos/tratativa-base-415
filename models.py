from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Vendedor(db.Model):
    __tablename__ = 'vendedores'
    codigo = db.Column(db.String(50), primary_key=True) # Código
    equipe = db.Column(db.String(100)) # Equipe
    vendedor_nome = db.Column(db.String(255)) # Vendedor
    filial = db.Column(db.String(100)) # Filial
    nome_completo = db.Column(db.String(255)) # Nome
    status = db.Column(db.String(50), default='Pendente') # Pendente, Sucesso, Erro, Vazio
    ultima_consulta = db.Column(db.DateTime)

class Comissao(db.Model):
    __tablename__ = 'comissoes'
    id = db.Column(db.Integer, primary_key=True)
    consulta_id = db.Column(db.String(100), index=True) # ID_Consulta único por lote
    vendedor_codigo = db.Column(db.String(50), db.ForeignKey('vendedores.codigo'))
    
    # Dados vindos do vendedor
    equipe = db.Column(db.String(100))
    codigo = db.Column(db.String(50))
    vendedor = db.Column(db.String(255))
    filial = db.Column(db.String(100))
    nome_vendedor = db.Column(db.String(255)) # Nome (do vendedor)
    
    # Dados extraídos do SSW
    clientes = db.Column(db.String(255))
    cnpj = db.Column(db.String(20))
    cidade = db.Column(db.String(100))
    nome_cliente = db.Column(db.String(255)) # Nome (do cliente extraído)
    
    conquista_inicio = db.Column(db.String(20))
    conquista_fim = db.Column(db.String(20))
    conquista_pct = db.Column(db.Float)
    
    manut_1_inicio = db.Column(db.String(20))
    manut_1_fim = db.Column(db.String(20))
    manut_1_pct = db.Column(db.Float)
    
    manut_2_inicio = db.Column(db.String(20))
    manut_2_fim = db.Column(db.String(20))
    manut_2_pct = db.Column(db.Float)
    
    mercadoria = db.Column(db.String(255))
    observacao = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
