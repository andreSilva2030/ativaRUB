from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.checkpoint_atividade import CheckpointAtividade
from models.atividade import Atividade
from models.loja import Loja
from database import db
from datetime import datetime

bp = Blueprint(
    'checkpoint_atividade',
    __name__,
    url_prefix='/checkpoint-atividades'
)

# =====================================================
# ROTAS WEB
# =====================================================

@bp.route('/')
def index():
    """
    Lista agrupada por nome_checkpoint
    """
    registros = (
        CheckpointAtividade.query
        .join(Atividade)
        .join(Loja)
        .order_by(
            CheckpointAtividade.nome_checkpoint.asc(),
            CheckpointAtividade.data_ini.desc()
        )
        .all()
    )

    return render_template(
        'checkpoint_atividade/index.html',
        registros=registros
    )


@bp.route('/create', methods=['GET', 'POST'])
def create():
    atividades = Atividade.query.order_by(Atividade.titulo).all()
    lojas = Loja.query.order_by(Loja.nome_loja).all()

    if request.method == 'POST':
        nome_checkpoint = request.form.get('nome_checkpoint')
        id_atividade = request.form.get('id_atividade', type=int)
        lojas_ids = request.form.getlist('lojas[]')
        status = request.form.get('status', 'Pendente')
        data_ini = request.form.get('data_ini')
        data_fim = request.form.get('data_fim')
        observacao = request.form.get('observacao')

        if not nome_checkpoint or not id_atividade or not lojas_ids or not data_ini:
            flash(
                'Checkpoint, atividade, lojas e data inicial são obrigatórios.',
                'danger'
            )
            return redirect(url_for('checkpoint_atividade.create'))

        try:
            for id_loja in lojas_ids:
                registro = CheckpointAtividade(
                    nome_checkpoint=nome_checkpoint,
                    id_atividade=id_atividade,
                    id_loja=int(id_loja),
                    status=status,
                    data_ini=datetime.fromisoformat(data_ini),
                    data_fim=datetime.fromisoformat(data_fim) if data_fim else None,
                    observacao=observacao
                )
                db.session.add(registro)

            db.session.commit()
            flash('Atividades do checkpoint registradas com sucesso!', 'success')
            return redirect(url_for('checkpoint_atividade.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar: {str(e)}', 'danger')

    return render_template(
        'checkpoint_atividade/create.html',
        atividades=atividades,
        lojas=lojas
    )


@bp.route('/<int:id>/edit')
def edit(id):
    registro = CheckpointAtividade.query.get_or_404(id)
    atividades = Atividade.query.order_by(Atividade.titulo).all()
    lojas = Loja.query.order_by(Loja.nome_loja).all()

    return render_template(
        'checkpoint_atividade/edit.html',
        registro=registro,
        atividades=atividades,
        lojas=lojas
    )


@bp.route('/<int:id>/update', methods=['POST'])
def update(id):
    registro = CheckpointAtividade.query.get_or_404(id)

    registro.nome_checkpoint = request.form.get(
        'nome_checkpoint',
        registro.nome_checkpoint
    )
    registro.status = request.form.get('status', registro.status)

    data_ini = request.form.get('data_ini')
    data_fim = request.form.get('data_fim')

    registro.data_ini = (
        datetime.fromisoformat(data_ini)
        if data_ini else registro.data_ini
    )

    registro.data_fim = (
        datetime.fromisoformat(data_fim)
        if data_fim else None
    )

    registro.observacao = request.form.get('observacao')

    try:
        db.session.commit()
        flash('Registro atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar: {str(e)}', 'danger')

    return redirect(url_for('checkpoint_atividade.index'))


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    registro = CheckpointAtividade.query.get_or_404(id)

    try:
        db.session.delete(registro)
        db.session.commit()
        flash('Registro removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir: {str(e)}', 'danger')

    return redirect(url_for('checkpoint_atividade.index'))

# =====================================================
# ROTAS API
# =====================================================

@bp.route('/api', methods=['GET'])
def api_index():
    registros = CheckpointAtividade.query.all()
    return jsonify([r.to_dict() for r in registros])


@bp.route('/api', methods=['POST'])
def api_create():
    data = request.get_json()

    required = ['nome_checkpoint', 'id_atividade', 'id_loja', 'data_ini']
    if not data or not all(k in data for k in required):
        return jsonify({'error': 'Campos obrigatórios ausentes'}), 400

    try:
        registro = CheckpointAtividade(
            nome_checkpoint=data['nome_checkpoint'],
            id_atividade=data['id_atividade'],
            id_loja=data['id_loja'],
            status=data.get('status', 'Pendente'),
            data_ini=datetime.fromisoformat(data['data_ini']),
            data_fim=(
                datetime.fromisoformat(data['data_fim'])
                if data.get('data_fim') else None
            ),
            observacao=data.get('observacao')
        )

        db.session.add(registro)
        db.session.commit()

        return jsonify(registro.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
