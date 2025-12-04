from database import db
from datetime import datetime

class GrupoTrabalho(db.Model):
    __tablename__ = 'grupotrabalho'
    
    id_grupo_trabalho = db.Column(db.Integer, primary_key=True)
    qtd_pessoas = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    id_responsavel = db.Column(db.Integer, db.ForeignKey('responsavel.id_responsavel'), unique=True)
    
    # Relacionamentos
    # 1:1 com Responsavel
    responsavel = db.relationship('Responsavel', back_populates='grupo_trabalho')
    
    # 1:N com Loja
    lojas = db.relationship('Loja', back_populates='grupo_trabalho', lazy=True)
    
    def __init__(self, qtd_pessoas=0, id_responsavel=None):
        self.qtd_pessoas = qtd_pessoas
        self.id_responsavel = id_responsavel
    
    def to_dict(self):
        return {
            'id_grupo_trabalho': self.id_grupo_trabalho,
            'qtd_pessoas': self.qtd_pessoas,
            'id_responsavel': self.id_responsavel,
            'responsavel_nome': self.responsavel.nome if self.responsavel else None,
            'total_lojas': len(self.lojas),
            'lojas_info': [{'id': loja.id_loja, 'nome': loja.nome_loja} for loja in self.lojas],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_total_sku_grupo(self):
        """Calcula o total de SKUs de todas as lojas do grupo"""
        return sum(loja.qtd_sku for loja in self.lojas)
    
    def __repr__(self):
        return f'<GrupoTrabalho (ID: {self.id_grupo_trabalho}) - {self.qtd_pessoas} pessoas>'