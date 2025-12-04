from database import db
from datetime import datetime

class Responsavel(db.Model):
    __tablename__ = 'responsavel'
    
    id_responsavel = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    contato = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento 1:1 com GrupoTrabalho
    grupo_trabalho = db.relationship('GrupoTrabalho', back_populates='responsavel', uselist=False)
    
    def __init__(self, nome, contato=None):
        self.nome = nome
        self.contato = contato
    
    def to_dict(self):
        return {
            'id_responsavel': self.id_responsavel,
            'nome': self.nome,
            'contato': self.contato,
            'grupo_trabalho_id': self.grupo_trabalho.id_grupo_trabalho if self.grupo_trabalho else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Responsavel {self.nome}>'