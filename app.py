from flask import Flask
from dotenv import load_dotenv
import os
from config import Config
from database import db, migrate
from controllers import divisao_bandeira_controller, loja_controller, responsavel_controller, checkpoint_atividade_controller, atividade_controller
from controllers.grupo_trabalho_controller import bp as grupo_trabalho_bp

# Carregar variáveis de ambiente
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar blueprints
    app.register_blueprint(divisao_bandeira_controller.bp)
    app.register_blueprint(loja_controller.bp)
    app.register_blueprint(responsavel_controller.bp)
    app.register_blueprint(grupo_trabalho_bp)
    app.register_blueprint(atividade_controller.bp)
    app.register_blueprint(checkpoint_atividade_controller.bp)
    
    # Rota principal
    @app.route('/')
    def index():
        return {'message': 'Ativa RUB - Gestao de rollout', 'status': 'online'}
    
    return app

# Criar a aplicação
app = create_app()