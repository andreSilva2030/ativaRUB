from database import db
from datetime import datetime

class Atividade(db.Model):
    __tablename__ = 'atividade'
    
    id_atividade = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pendente')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento N:N com Loja (através da tabela de junção)
    lojas = db.relationship(
        'Loja',
        secondary='atividade_loja',
        back_populates='atividades',
        lazy='dynamic'
    )
    
    def __init__(self, titulo, descricao=None, status='Pendente'):
        self.titulo = titulo
        self.descricao = descricao
        self.status = status
    
    def to_dict(self):
        return {
            'id_atividade': self.id_atividade,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'status': self.status,
            'total_lojas': self.lojas.count() if hasattr(self.lojas, 'count') else len(self.lojas),
            'lojas_vinculadas': [{'id': loja.id_loja, 'nome': loja.nome_loja} for loja in self.lojas],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def adicionar_loja(self, loja):
        """Adiciona uma loja à atividade"""
        if loja not in self.lojas:
            self.lojas.append(loja)
            return True
        return False
    
    def remover_loja(self, loja):
        """Remove uma loja da atividade"""
        if loja in self.lojas:
            self.lojas.remove(loja)
            return True
        return False
    
    def get_lojas_por_divisao(self):
        """Agrupa lojas por divisão/bandeira"""
        divisoes = {}
        for loja in self.lojas:
            divisao_nome = loja.divisao_bandeira.nome_bandeira if loja.divisao_bandeira else 'Sem Divisão'
            if divisao_nome not in divisoes:
                divisoes[divisao_nome] = []
            divisoes[divisao_nome].append(loja.nome_loja)
        return divisoes
    
    def __repr__(self):
        return f'<Atividade {self.titulo} ({self.status})>'