from database import db
from datetime import datetime

class Atividade(db.Model):
    __tablename__ = 'atividade'

    id_atividade = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relacionamento com CheckpointAtividade (execuções)
    checkpoint_atividades = db.relationship(
        'CheckpointAtividade',
        back_populates='atividade',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Atividade {self.id_atividade} - {self.titulo}>'

    def to_dict(self):
        return {
            'id_atividade': self.id_atividade,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
