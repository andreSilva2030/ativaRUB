from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.planejamento import Planejamento
from models.atividade import Atividade
from models.grupo_trabalho import GrupoTrabalho
from database import db
from datetime import datetime

bp = Blueprint(
    'planejamento',
    __name__,
    url_prefix='/planejamentos'
)

# =====================================================
# ROTAS WEB
# =====================================================

@bp.route('/')
def index():
    planejamentos = (
        Planejamento.query
        .join(Atividade)
        .join(GrupoTrabalho)
        .order_by(
            Planejamento.data_ini.desc(),
            Planejamento.titulo.asc()
        )
        .all()
    )

    return render_template(
        'planejamento/index.html',
        planejamentos=planejamentos
    )


@bp.route('/create', methods=['GET', 'POST'])
def create():
    atividades = Atividade.query.order_by(Atividade.titulo).all()
    grupos_trabalho = (
        GrupoTrabalho.query.order_by(GrupoTrabalho.nome_grupo).all()
    )

    if request.method == 'POST':
        titulo_plano = request.form.get('titulo')
        id_atividade = request.form.get('id_atividade', type=int)
        id_grupo_trabalho = request.form.get(
            'id_grupo_trabalho', type=int
        )
        data_ini = request.form.get('data_ini')
        data_fim = request.form.get('data_fim')

        if not all([titulo_plano, id_atividade, id_grupo_trabalho, data_ini]):
            flash(
                'Título, atividade, grupo de trabalho e data inicial são obrigatórios.',
                'danger'
            )
            return redirect(url_for('planejamento.create'))

        try:
            planejamento = Planejamento(
                titulo=titulo_plano,
                id_atividade=id_atividade,
                id_grupo_trabalho=id_grupo_trabalho,
                data_ini=datetime.fromisoformat(data_ini),
                data_fim=(
                    datetime.fromisoformat(data_fim)
                    if data_fim else None
                )
            )

            db.session.add(planejamento)
            db.session.commit()

            flash('Planejamento criado com sucesso!', 'success')
            return redirect(url_for('planejamento.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar: {str(e)}', 'danger')

    return render_template(
        'planejamento/create.html',
        atividades=atividades,
        grupos_trabalho=grupos_trabalho
    )


@bp.route('/<int:id>/edit')
def edit(id):
    planejamento = Planejamento.query.get_or_404(id)
    atividades = Atividade.query.order_by(Atividade.titulo).all()
    grupos_trabalho = (
        GrupoTrabalho.query.order_by(GrupoTrabalho.nome_grupo).all()
    )

    return render_template(
        'planejamento/edit.html',
        planejamento=planejamento,
        atividades=atividades,
        grupos_trabalho=grupos_trabalho
    )


@bp.route('/<int:id>/update', methods=['POST'])
def update(id):
    planejamento = Planejamento.query.get_or_404(id)

    planejamento.titulo = request.form.get(
        'titulo', planejamento.titulo
    )

    planejamento.id_atividade = request.form.get(
        'id_atividade', planejamento.id_atividade, type=int
    )

    planejamento.id_grupo_trabalho = request.form.get(
        'id_grupo_trabalho',
        planejamento.id_grupo_trabalho,
        type=int
    )

    data_ini = request.form.get('data_ini')
    data_fim = request.form.get('data_fim')

    planejamento.data_ini = (
        datetime.fromisoformat(data_ini)
        if data_ini else planejamento.data_ini
    )

    planejamento.data_fim = (
        datetime.fromisoformat(data_fim)
        if data_fim else None
    )

    try:
        db.session.commit()
        flash('Planejamento atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar: {str(e)}', 'danger')

    return redirect(url_for('planejamento.index'))


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    planejamento = Planejamento.query.get_or_404(id)

    try:
        db.session.delete(planejamento)
        db.session.commit()
        flash('Planejamento removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir: {str(e)}', 'danger')

    return redirect(url_for('planejamento.index'))

# =====================================================
# ROTAS API
# =====================================================

@bp.route('/api', methods=['GET'])
def api_index():
    planejamentos = Planejamento.query.all()
    return jsonify([p.to_dict() for p in planejamentos])


@bp.route('/api', methods=['POST'])
def api_create():
    data = request.get_json()

    required = [
        'titulo',
        'id_atividade',
        'id_grupo_trabalho',
        'data_ini'
    ]

    if not data or not all(k in data for k in required):
        return jsonify({'error': 'Campos obrigatórios ausentes'}), 400

    try:
        planejamento = Planejamento(
            titulo=data['titulo'],
            id_atividade=data['id_atividade'],
            id_grupo_trabalho=data['id_grupo_trabalho'],
            data_ini=datetime.fromisoformat(data['data_ini']),
            data_fim=(
                datetime.fromisoformat(data['data_fim'])
                if data.get('data_fim') else None
            )
        )

        db.session.add(planejamento)
        db.session.commit()

        return jsonify(planejamento.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
