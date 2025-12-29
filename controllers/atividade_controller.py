from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.atividade import Atividade
from database import db

bp = Blueprint('atividade', __name__, url_prefix='/atividades')

# ========== ROTAS WEB ==========

@bp.route('/', methods=['GET'])
def listar_atividades():
    atividades = Atividade.query.order_by(Atividade.titulo).all()
    return render_template('atividade/index.html', atividades=atividades)


@bp.route('/<int:id_atividade>', methods=['GET'])
def obter_atividade(id_atividade):
    atividade = Atividade.query.get_or_404(id_atividade)
    return render_template(
        'atividade/show.html',
        atividade=atividade
    )

@bp.route('/create', methods=['GET', 'POST'])
def nova_atividade():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')

        if not titulo:
            flash('O título é obrigatório.', 'danger')
            return redirect(url_for('atividade.nova_atividade'))

        atividade = Atividade(
            titulo=titulo,
            descricao=descricao
        )

        try:
            db.session.add(atividade)
            db.session.commit()
            flash('Atividade criada com sucesso!', 'success')
            return redirect(url_for('atividade.listar_atividades'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar atividade: {str(e)}', 'danger')

    return render_template('atividade/create.html')


@bp.route('/<int:id_atividade>/edit', methods=['GET', 'POST'])
def editar_atividade(id_atividade):
    atividade = Atividade.query.get_or_404(id_atividade)

    if request.method == 'POST':
        atividade.titulo = request.form.get('titulo')
        atividade.descricao = request.form.get('descricao')

        try:
            db.session.commit()
            flash('Atividade atualizada com sucesso!', 'success')
            return redirect(url_for('atividade.listar_atividades'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar atividade: {str(e)}', 'danger')

    return render_template('atividade/edit.html', atividade=atividade)


@bp.route('/<int:id_atividade>/delete', methods=['POST'])
def excluir_atividade(id_atividade):
    atividade = Atividade.query.get_or_404(id_atividade)

    try:
        db.session.delete(atividade)
        db.session.commit()
        flash('Atividade excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir atividade: {str(e)}', 'danger')

    return redirect(url_for('atividade.listar_atividades'))



# ========== ROTAS API ==========

@bp.route('/api', methods=['GET'])
def api_listar_atividades():
    atividades = Atividade.query.all()
    return jsonify([atividade.to_dict() for atividade in atividades]), 200


@bp.route('/api/<int:id_atividade>', methods=['GET'])
def api_obter_atividade(id_atividade):
    atividade = Atividade.query.get_or_404(id_atividade)
    return jsonify(atividade.to_dict()), 200


@bp.route('/api', methods=['POST'])
def api_criar_atividade():
    data = request.get_json()

    if not data or 'titulo' not in data:
        return jsonify({'error': 'O campo título é obrigatório'}), 400

    atividade = Atividade(
        titulo=data['titulo'],
        descricao=data.get('descricao')
    )

    try:
        db.session.add(atividade)
        db.session.commit()
        return jsonify(atividade.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:id_atividade>', methods=['PUT'])
def api_atualizar_atividade(id_atividade):
    atividade = Atividade.query.get_or_404(id_atividade)
    data = request.get_json()

    if 'titulo' in data:
        atividade.titulo = data['titulo']
    if 'descricao' in data:
        atividade.descricao = data['descricao']

    try:
        db.session.commit()
        return jsonify(atividade.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/<int:id_atividade>', methods=['DELETE'])
def api_excluir_atividade(id_atividade):
    atividade = Atividade.query.get_or_404(id_atividade)

    try:
        db.session.delete(atividade)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
