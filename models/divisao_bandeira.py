from database import db
from datetime import datetime

class DivisaoBandeira(db.Model):
    __tablename__ = 'divisao_bandeira'
    
    id_bandeira_divisao = db.Column(db.Integer, primary_key=True)
    nome_bandeira = db.Column(db.String(255), nullable=False)
    contato = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento 1:N com Loja
    lojas = db.relationship('Loja', back_populates='divisao_bandeira')
    
    def __init__(self, nome_bandeira, contato=None):
        self.nome_bandeira = nome_bandeira
        self.contato = contato
    
    def to_dict(self):
        return {
            'id_bandeira_divisao': self.id_bandeira_divisao,
            'nome_bandeira': self.nome_bandeira,
            'contato': self.contato,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_lojas': len(self.lojas) if self.lojas else 0
        }
    
    def __repr__(self):
        return f'<DivisaoBandeira {self.nome_bandeira}>'