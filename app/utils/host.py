class HostUtils(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.host = None

    def init_app(self, app):
        print('Init host')
        self.host = app.config.get('BACKEND_URL')