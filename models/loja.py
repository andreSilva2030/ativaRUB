from database import db
from datetime import datetime

class Loja(db.Model):
    __tablename__ = 'loja'

    id_loja = db.Column(db.Integer, primary_key=True)
    nome_loja = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.Text)

    qtd_sku = db.Column(db.Integer, default=0)
    qtd_pessoas = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Foreign Keys
    id_divisao_bandeira = db.Column(
        db.Integer,
        db.ForeignKey('divisao_bandeira.id_bandeira_divisao'),
        nullable=False
    )

    id_grupo_trabalho = db.Column(
        db.Integer,
        db.ForeignKey('grupo_trabalho.id_grupo_trabalho')
    )

    # Relacionamentos
    divisao_bandeira = db.relationship(
        'DivisaoBandeira',
        back_populates='lojas'
    )

    grupo_trabalho = db.relationship(
        'GrupoTrabalho',
        back_populates='lojas'
    )

    # Execuções de atividades (via checkpoint)
    checkpoint_atividades = db.relationship(
        'CheckpointAtividade',
        back_populates='loja',
        cascade='all, delete-orphan'
    )

    def __init__(
        self,
        nome_loja,
        endereco=None,
        qtd_sku=0,
        qtd_pessoas=0,
        id_divisao_bandeira=None,
        id_grupo_trabalho=None
    ):
        self.nome_loja = nome_loja
        self.endereco = endereco
        self.qtd_sku = qtd_sku
        self.qtd_pessoas = qtd_pessoas
        self.id_divisao_bandeira = id_divisao_bandeira
        self.id_grupo_trabalho = id_grupo_trabalho

    def __repr__(self):
        return f'<Loja {self.nome_loja} (ID: {self.id_loja})>'

    def to_dict(self):
        return {
            'id_loja': self.id_loja,
            'nome_loja': self.nome_loja,
            'endereco': self.endereco,
            'qtd_sku': self.qtd_sku,
            'qtd_pessoas': self.qtd_pessoas,
            'id_divisao_bandeira': self.id_divisao_bandeira,
            'id_grupo_trabalho': self.id_grupo_trabalho,
            'divisao_bandeira_nome': (
                self.divisao_bandeira.nome_bandeira
                if self.divisao_bandeira else None
            ),
            'grupo_trabalho': {
                'id': self.grupo_trabalho.id_grupo_trabalho,
                'nome': self.grupo_trabalho.nome_grupo
            } if self.grupo_trabalho else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
