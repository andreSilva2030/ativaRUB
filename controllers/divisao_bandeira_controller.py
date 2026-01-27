from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models import DivisaoBandeira, GrupoTrabalho
from database import db

bp = Blueprint('divisao_bandeira', __name__, url_prefix='/divisao_bandeira')

# ========== ROTAS WEB (HTML) ==========

@bp.route('/')
def index():
    """Lista todas as divisões/bandeiras"""
    divisoes = DivisaoBandeira.query.order_by(DivisaoBandeira.nome_bandeira).all()
    return render_template('divisao_bandeira/index.html', divisoes=divisoes)  # Remova a barra inicial

@bp.route('/create', methods=['GET', 'POST'])
def create():
    """Cria uma nova divisão/bandeira"""
    if request.method == 'POST':
        nome_bandeira = request.form.get('nome_bandeira')
        contato = request.form.get('contato')
        
        if not nome_bandeira:
            flash('Nome da bandeira é obrigatório!', 'error')
            return render_template('divisao_bandeira/create.html')
        
        # Verifica se já existe
        existe = DivisaoBandeira.query.filter_by(nome_bandeira=nome_bandeira).first()
        if existe:
            flash('Já existe uma divisão/bandeira com este nome!', 'error')
            return render_template('divisao_bandeira/create.html')
        
        nova_divisao = DivisaoBandeira(nome_bandeira=nome_bandeira, contato=contato)
        
        try:
            db.session.add(nova_divisao)
            db.session.commit()
            flash('Divisão/Bandeira criada com sucesso!', 'success')
            return redirect(url_for('divisao_bandeira.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar: {str(e)}', 'error')
    
    return render_template('divisao_bandeira/create.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edita uma divisão/bandeira existente"""
    divisao = DivisaoBandeira.query.get_or_404(id)
    
    if request.method == 'POST':
        nome_bandeira = request.form.get('nome_bandeira')
        contato = request.form.get('contato')
        
        if not nome_bandeira:
            flash('Nome da bandeira é obrigatório!', 'error')
            return render_template('divisao_bandeira/edit.html', divisao=divisao)
        
        # Verifica se o novo nome já existe (excluindo o atual)
        existe = DivisaoBandeira.query.filter(
            DivisaoBandeira.nome_bandeira == nome_bandeira,
            DivisaoBandeira.id_bandeira_divisao != id
        ).first()
        
        if existe:
            flash('Já existe outra divisão/bandeira com este nome!', 'error')
            return render_template('divisao_bandeira/edit.html', divisao=divisao)
        
        divisao.nome_bandeira = nome_bandeira
        divisao.contato = contato
        
        try:
            db.session.commit()
            flash('Divisão/Bandeira atualizada com sucesso!', 'success')
            return redirect(url_for('divisao_bandeira.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {str(e)}', 'error')
    
    return render_template('divisao_bandeira/edit.html', divisao=divisao)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Exclui uma divisão/bandeira"""
    divisao = DivisaoBandeira.query.get_or_404(id)
    
    # Verifica se existem lojas vinculadas
    if divisao.lojas:
        flash('Não é possível excluir esta divisão pois existem lojas vinculadas!', 'error')
        return redirect(url_for('divisao_bandeira.index'))
    
    try:
        db.session.delete(divisao)
        db.session.commit()
        flash('Divisão/Bandeira excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir: {str(e)}', 'error')
    
    return redirect(url_for('divisao_bandeira.index'))

@bp.route('/<int:id>')
def show(id):
    """Exibe detalhes de uma divisão/bandeira"""
    divisao = DivisaoBandeira.query.get_or_404(id)
    return render_template('divisao_bandeira/show.html', divisao=divisao)

# ========== ROTAS API (JSON) ==========

@bp.route('/api', methods=['GET'])
def api_index():
    """API: Lista todas as divisões/bandeiras (JSON)"""
    divisoes = DivisaoBandeira.query.all()
    return jsonify([divisao.to_dict() for divisao in divisoes])

@bp.route('/api/<int:id>', methods=['GET'])
def api_show(id):
    """API: Retorna uma divisão/bandeira específica (JSON)"""
    divisao = DivisaoBandeira.query.get_or_404(id)
    return jsonify(divisao.to_dict())

@bp.route('/api', methods=['POST'])
def api_create():
    """API: Cria uma nova divisão/bandeira (JSON)"""
    data = request.get_json()
    
    if not data or 'nome_bandeira' not in data:
        return jsonify({'error': 'Nome da bandeira é obrigatório'}), 400
    
    existe = DivisaoBandeira.query.filter_by(nome_bandeira=data['nome_bandeira']).first()
    if existe:
        return jsonify({'error': 'Divisão/Bandeira já existe'}), 409
    
    nova_divisao = DivisaoBandeira(
        nome_bandeira=data['nome_bandeira'],
        contato=data.get('contato')
    )
    
    try:
        db.session.add(nova_divisao)
        db.session.commit()
        return jsonify(nova_divisao.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/<int:id>', methods=['PUT'])
def api_update(id):
    """API: Atualiza uma divisão/bandeira (JSON)"""
    divisao = DivisaoBandeira.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
    
    if 'nome_bandeira' in data:
        # Verifica se o novo nome já existe
        existe = DivisaoBandeira.query.filter(
            DivisaoBandeira.nome_bandeira == data['nome_bandeira'],
            DivisaoBandeira.id_bandeira_divisao != id
        ).first()
        
        if existe:
            return jsonify({'error': 'Outra divisão já usa este nome'}), 409
        
        divisao.nome_bandeira = data['nome_bandeira']
    
    if 'contato' in data:
        divisao.contato = data['contato']
    
    try:
        db.session.commit()
        return jsonify(divisao.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete(id):
    """API: Exclui uma divisão/bandeira (JSON)"""
    divisao = DivisaoBandeira.query.get_or_404(id)
    
    if divisao.lojas:
        return jsonify({'error': 'Existem lojas vinculadas a esta divisão'}), 409
    
    try:
        db.session.delete(divisao)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500