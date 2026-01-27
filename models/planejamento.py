from database import db
from datetime import datetime


class Planejamento(db.Model):
    __tablename__ = 'planejamento'

    id_planejamento = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(255), nullable=False)
    data_ini = db.Column(db.DateTime, default=datetime)
    data_fim = db.Column(db.DateTime, default=datetime)

    # FKs
    id_grupo_trabalho = db.Column(
        db.Integer,
        db.ForeignKey('grupo_trabalho.id_grupo_trabalho'),
        nullable=False
    )

    id_atividade = db.Column(
        db.Integer,
        db.ForeignKey('atividade.id_atividade'),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    status = db.Column(
        db.String(50),
        default='Pendente'
    )

    # Relacionamentos
    atividade = db.relationship(
        'Atividade',
        backref=db.backref('planejamentos', lazy=True)
    )
    
    grupo_trabalho = db.relationship(
        'GrupoTrabalho',
        back_populates='planejamentos'
    )

    checkpoint_atividades = db.relationship(
        'CheckpointAtividade',
        back_populates='planejamento',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return (
            f'<Planejamento {self.id_planejamento} - {self.titulo_plano}>'
        )

    def to_dict(self):
        return {
            'id_planejamento': self.id_planejamento,
            'titulo': self.titulo,
            'data_ini': self.data_ini.isoformat() if self.data_ini else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'id_grupo_trabalho': self.id_grupo_trabalho,
            'id_atividade': self.id_atividade,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def atualizar_status(self):
        """
        Atualiza o status do planejamento com base nos checkpoints relacionados.
        """
        if any(checkpoint.status == 'Concluído' for checkpoint in self.checkpoint_atividades):
            self.status = 'Concluído'
        else:
            self.status = 'Pendente'
