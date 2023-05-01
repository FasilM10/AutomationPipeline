import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    #configuration variables...

    @staticmethod
    def init_app(app):
        pass

class DevConfig(Config):
    DB_PORT = os.environ.get('DB_PORT', 3306)
    SERVER_URI = os.environ.get('SERVER_URI', "")
    DB_NAME = os.environ.get('DB_NAME', "")
    DB_USER_NAME = os.environ.get('DB_USER_NAME', "")
    DB_USER_PASS = os.environ.get('DB_USER_PASS', "")

class TestConfig(Config):
    DB_PORT = os.environ.get('DB_PORT', 3306)
    SERVER_URI = os.environ.get('SERVER_URI', "")
    DB_NAME = os.environ.get('DB_NAME', "")
    DB_USER_NAME = os.environ.get('DB_USER_NAME', "")
    DB_USER_PASS = os.environ.get('DB_USER_PASS', "")

class ProdConfig(Config):
    DB_PORT = os.environ.get('DB_PORT', 3306)
    SERVER_URI = os.environ.get('SERVER_URI', "")
    DB_NAME = os.environ.get('DB_NAME', "")
    DB_USER_NAME = os.environ.get('DB_USER_NAME', "")
    DB_USER_PASS = os.environ.get('DB_USER_PASS', "")

config = {
    'dev' : DevConfig,
    'test' : TestConfig,
    'prod' : ProdConfig,
    'default' : DevConfig
}