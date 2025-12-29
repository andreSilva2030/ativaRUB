from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models import Loja, DivisaoBandeira, GrupoTrabalho
from database import db

bp = Blueprint('lojas', __name__, url_prefix='/lojas')

# ========== ROTAS WEB ==========

@bp.route('/')
def index():
    lojas = Loja.query.order_by(Loja.nome_loja).all()
    return render_template('lojas/index.html', lojas=lojas)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    divisoes = DivisaoBandeira.query.all()
    grupos = GrupoTrabalho.query.all()

    if request.method == 'POST':
        nome_loja = request.form.get('nome_loja')
        endereco = request.form.get('endereco')
        qtd_sku = request.form.get('qtd_sku', type=int)
        qtd_pessoas = request.form.get('qtd_pessoas', type=int)
        id_divisao_bandeira = request.form.get('id_divisao_bandeira', type=int)
        id_grupo_trabalho = request.form.get('id_grupo_trabalho', type=int)

        if not nome_loja or not id_divisao_bandeira:
            flash('Nome da loja e divisão/bandeira são obrigatórios!', 'error')
            return render_template(
                'lojas/create.html',
                divisoes=divisoes,
                grupos=grupos
            )

        loja = Loja(
            nome_loja=nome_loja,
            endereco=endereco,
            qtd_sku=qtd_sku or 0,
            qtd_pessoas=qtd_pessoas or 0,
            id_divisao_bandeira=id_divisao_bandeira,
            id_grupo_trabalho=id_grupo_trabalho
        )

        try:
            db.session.add(loja)
            db.session.commit()
            flash('Loja criada com sucesso!', 'success')
            return redirect(url_for('lojas.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar loja: {str(e)}', 'error')

    return render_template('lojas/create.html', divisoes=divisoes, grupos=grupos)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    loja = Loja.query.get_or_404(id)
    divisoes = DivisaoBandeira.query.all()
    grupos = GrupoTrabalho.query.all()

    if request.method == 'POST':
        loja.nome_loja = request.form.get('nome_loja')
        loja.endereco = request.form.get('endereco')
        loja.qtd_sku = request.form.get('qtd_sku', type=int) or 0
        loja.qtd_pessoas = request.form.get('qtd_pessoas', type=int) or 0
        loja.id_divisao_bandeira = request.form.get('id_divisao_bandeira', type=int)
        loja.id_grupo_trabalho = request.form.get('id_grupo_trabalho', type=int)

        try:
            db.session.commit()
            flash('Loja atualizada com sucesso!', 'success')
            return redirect(url_for('lojas.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar loja: {str(e)}', 'error')

    return render_template(
        'lojas/edit.html',
        loja=loja,
        divisoes=divisoes,
        grupos=grupos
    )


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    loja = Loja.query.get_or_404(id)
    try:
        db.session.delete(loja)
        db.session.commit()
        flash('Loja excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir loja: {str(e)}', 'error')
    return redirect(url_for('lojas.index'))


@bp.route('/<int:id>')
def show(id):
    loja = Loja.query.get_or_404(id)
    return render_template('lojas/show.html', loja=loja)


# ========== ROTAS API ==========

@bp.route('/api', methods=['GET'])
def api_index():
    lojas = Loja.query.all()
    return jsonify([loja.to_dict() for loja in lojas])


@bp.route('/api/<int:id>', methods=['GET'])
def api_show(id):
    loja = Loja.query.get_or_404(id)
    return jsonify(loja.to_dict())


@bp.route('/api', methods=['POST'])
def api_create():
    data = request.get_json()

    if not data or 'nome_loja' not in data or 'id_divisao_bandeira' not in data:
        return jsonify({'error': 'Nome da loja e divisão/bandeira são obrigatórios'}), 400

    loja = Loja(
        nome_loja=data['nome_loja'],
        endereco=data.get('endereco'),
        qtd_sku=data.get('qtd_sku', 0),
        qtd_pessoas=data.get('qtd_pessoas', 0),
        id_divisao_bandeira=data['id_divisao_bandeira'],
        id_grupo_trabalho=data.get('id_grupo_trabalho')
    )

    try:
        db.session.add(loja)
        db.session.commit()
        return jsonify(loja.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:id>', methods=['PUT'])
def api_update(id):
    loja = Loja.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    for field in [
        'nome_loja', 'endereco', 'qtd_sku',
        'qtd_pessoas', 'id_divisao_bandeira',
        'id_grupo_trabalho'
    ]:
        if field in data:
            setattr(loja, field, data[field])

    try:
        db.session.commit()
        return jsonify(loja.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:id>', methods=['DELETE'])
def api_delete(id):
    loja = Loja.query.get_or_404(id)
    try:
        db.session.delete(loja)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
