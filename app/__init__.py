from flask import Flask
from flask_bootstrap import Bootstrap
from config import config
from .utils.host import HostUtils

bootstrap = Bootstrap()
host_utils = HostUtils()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app=app)
    host_utils.init_app(app=app)
    bootstrap.init_app(app=app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app