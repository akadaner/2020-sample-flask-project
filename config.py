import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rfc_project_88888888'
    @staticmethod
    def init_app(app):
        pass


class DebugConfig(Config):
    BACKEND_URL = 'http://0.0.0.0:8818/api'

    @staticmethod
    def init_app(app):
        Config.init_app(app)


class ProductionConfig(Config):
    BACKEND_URL = os.environ.get('BACKEND_URL')

    @staticmethod
    def init_app(app):
        Config.init_app(app)


config = {
    'production': ProductionConfig,
    'default': ProductionConfig,
    'debug': DebugConfig
}