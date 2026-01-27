from database import db
from datetime import datetime

class GrupoTrabalho(db.Model):
    __tablename__ = 'grupo_trabalho'
    
    id_grupo_trabalho = db.Column(db.Integer, primary_key=True)
    nome_grupo = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    id_responsavel = db.Column(db.Integer, db.ForeignKey('responsavel.id_responsavel'))
    
    # Relacionamentos
    # N:1 com Responsavel
    responsavel = db.relationship('Responsavel', back_populates='grupos_trabalho', lazy='joined')
    
    # 1:N com Loja
    lojas = db.relationship('Loja', back_populates='grupo_trabalho', lazy=True)
    
    planejamentos = db.relationship(
        'Planejamento',
        back_populates='grupo_trabalho',
        cascade='all, delete-orphan'
    )

    def __init__(self, nome_grupo, id_responsavel=None):
        self.nome_grupo = nome_grupo
        self.id_responsavel = id_responsavel
    
    def to_dict(self):
        return {
            'id_grupo_trabalho': self.id_grupo_trabalho,
            'nome_grupo': self.nome_grupo,
            'id_responsavel': self.id_responsavel,
            'responsavel_nome': self.responsavel.nome if self.responsavel else None,
            'total_lojas': len(self.lojas),
            'total_pessoas': self.calculate_total_pessoas(),  # Inclui o cálculo de total_pessoas
            'lojas_info': [
                {
                    'id': loja.id_loja,
                    'nome': loja.nome_loja,
                    'qtd_pessoas': loja.qtd_pessoas
                }
                for loja in self.lojas
            ],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_total_pessoas(self):
        """Calcula o total de pessoas somando qtd_pessoas de todas as lojas associadas."""
        return sum(loja.qtd_pessoas for loja in self.lojas)

    def __repr__(self):
        return f'<GrupoTrabalho (ID: {self.id_grupo_trabalho}) - {self.nome_grupo}>'