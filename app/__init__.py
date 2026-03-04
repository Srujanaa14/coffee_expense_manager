from flask import Flask
from .config import config_by_name
from .extensions import db, login_manager, migrate


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate detects them
    with app.app_context():
        from app.models import User, Farm, Expense, Income

    # Register blueprints
    from .routes.auth      import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.expenses  import expenses_bp
    from .routes.farms     import farms_bp
    from .routes.reports   import reports_bp
    from .routes.income    import income_bp

    app.register_blueprint(auth_bp,      url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(expenses_bp,  url_prefix="/expenses")
    app.register_blueprint(farms_bp,     url_prefix="/farms")
    app.register_blueprint(reports_bp,   url_prefix="/reports")
    app.register_blueprint(income_bp,    url_prefix="/income")

    return app