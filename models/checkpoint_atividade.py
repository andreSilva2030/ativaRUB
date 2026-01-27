from database import db
from datetime import datetime


class CheckpointAtividade(db.Model):
    __tablename__ = 'checkpoint_atividade'

    id_checkpoint_atividade = db.Column(db.Integer, primary_key=True)

    # Identificação lógica do checkpoint
    nome_checkpoint = db.Column(
        db.String(150),
        nullable=False
    )

    id_loja = db.Column(
        db.Integer,
        db.ForeignKey('loja.id_loja'),
        nullable=False
    )

    id_planejamento = db.Column(
        db.Integer,
        db.ForeignKey('planejamento.id_planejamento'),
        nullable=False
    )

    # Status da execução
    status = db.Column(
        db.String(50),
        nullable=False,
        default='Pendente'
    )

    # Controle de tempo
    data_ini = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime)

    # Observações / comentários
    observacao = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relacionamentos
    loja = db.relationship('Loja')
    planejamento = db.relationship('Planejamento')

    def __repr__(self):
        return (
            f'<CheckpointAtividade '
            f'CP:"{self.nome_checkpoint}" '
            f'LO:{self.id_loja} '
            f'ST:{self.status}>'
        )

    @property
    def tempo_gasto_segundos(self):
        """
        Retorna o tempo gasto em segundos
        """
        if self.data_ini and self.data_fim:
            return (self.data_fim - self.data_ini).total_seconds()
        return None

    @property
    def tempo_gasto_horas(self):
        """
        Retorna o tempo gasto em horas
        """
        if self.data_ini and self.data_fim:
            return round(
                (self.data_fim - self.data_ini).total_seconds() / 3600, 2
            )
        return None

    def to_dict(self):
        return {
            'id_checkpoint_atividade': self.id_checkpoint_atividade,

            'nome_checkpoint': self.nome_checkpoint,
            'loja': {
                'id': self.loja.id_loja,
                'nome': self.loja.nome_loja
            } if self.loja else None,
            'id_planejamento': self.id_planejamento,
            'status': self.status,
            'data_ini': self.data_ini.isoformat() if self.data_ini else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'tempo_gasto_segundos': self.tempo_gasto_segundos,
            'tempo_gasto_horas': self.tempo_gasto_horas,
            'observacao': self.observacao,

            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def atualizar_planejamento_status(self):
        """
        Atualiza o status do planejamento relacionado.
        """
        if self.planejamento:
            self.planejamento.atualizar_status()
            db.session.commit()

    # Sobrescrever o método save para garantir a atualização
    def save(self):
        """
        Salva o checkpoint e atualiza o planejamento relacionado.
        """
        db.session.add(self)
        db.session.commit()
        self.atualizar_planejamento_status()
