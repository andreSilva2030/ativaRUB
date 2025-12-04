from database import db
from datetime import datetime

# Tabela de junção para relação N:N entre Atividade e Loja
atividade_loja = db.Table('atividade_loja',
    db.Column('id_atividade_loja', db.Integer, primary_key=True),
    db.Column('id_atividade', db.Integer, db.ForeignKey('atividade.id_atividade'), nullable=False),
    db.Column('id_loja', db.Integer, db.ForeignKey('loja.id_loja'), nullable=False),
    db.Column('data_vinculo', db.DateTime, default=datetime.utcnow),
    db.UniqueConstraint('id_atividade', 'id_loja', name='uniq_atividade_loja')
)

class Loja(db.Model):
    __tablename__ = 'loja'
    
    id_loja = db.Column(db.Integer, primary_key=True)
    nome_loja = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.Text)
    qtd_sku = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    id_divisao_bandeira = db.Column(db.Integer, db.ForeignKey('divisaobandeira.id_bandeira_divisao'), nullable=False)
    id_grupo_trabalho = db.Column(db.Integer, db.ForeignKey('grupotrabalho.id_grupo_trabalho'))
    
    # Relacionamentos
    # 1. Relação com DivisaoBandeira (M:1)
    divisao_bandeira = db.relationship(
        'DivisaoBandeira',
        back_populates='lojas',  # troque backref por back_populates
        overlaps="divisao"
    )
    
    # 2. Relação com GrupoTrabalho (M:1)
    grupo_trabalho = db.relationship('GrupoTrabalho', back_populates='lojas')
    
    # 3. Relação N:N com Atividade (através da tabela de junção)
    atividades = db.relationship(
        'Atividade',
        secondary=atividade_loja,
        back_populates='lojas',
        lazy='dynamic'
    )
    
    def __init__(self, nome_loja, endereco=None, qtd_sku=0, id_divisao_bandeira=None, id_grupo_trabalho=None):
        self.nome_loja = nome_loja
        self.endereco = endereco
        self.qtd_sku = qtd_sku
        self.id_divisao_bandeira = id_divisao_bandeira
        self.id_grupo_trabalho = id_grupo_trabalho
    
    def to_dict(self):
        return {
            'id_loja': self.id_loja,
            'nome_loja': self.nome_loja,
            'endereco': self.endereco,
            'qtd_sku': self.qtd_sku,
            'id_divisao_bandeira': self.id_divisao_bandeira,
            'id_grupo_trabalho': self.id_grupo_trabalho,
            'divisao_bandeira_nome': self.divisao_bandeira.nome_bandeira if self.divisao_bandeira else None,
            'grupo_trabalho_info': {
                'id': self.grupo_trabalho.id_grupo_trabalho if self.grupo_trabalho else None,
                'qtd_pessoas': self.grupo_trabalho.qtd_pessoas if self.grupo_trabalho else None
            } if self.grupo_trabalho else None,
            'total_atividades': self.atividades.count() if hasattr(self.atividades, 'count') else len(self.atividades),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_atividades_info(self):
        """Retorna informações das atividades vinculadas"""
        atividades_info = []
        for atividade in self.atividades:
            atividades_info.append({
                'id': atividade.id_atividade,
                'titulo': atividade.titulo,
                'status': atividade.status
            })
        return atividades_info
    
    def __repr__(self):
        return f'<Loja {self.nome_loja} (ID: {self.id_loja})>'