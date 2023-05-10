from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        # Create the database tables
        db.create_all()

    # Register blueprints
    from .controller.employees import employees_blueprint
    app.register_blueprint(employees_blueprint)

    from .controller.jobs import jobs_blueprint
    app.register_blueprint(jobs_blueprint)

    from .controller.departments import departments_blueprint
    app.register_blueprint(departments_blueprint)

    from .controller.database_utilities import database_utilities_blueprint
    app.register_blueprint(database_utilities_blueprint)

    return app