import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'correct horse stable battery',
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(app.instance_path, 'task_list.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )
    from . import music_queue
    app.register_blueprint(music_queue.bp)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models

    return app
