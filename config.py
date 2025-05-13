class Config(object):
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "iejszfseozikwiojeav893278JWHIEgyweielmao"
    
class DevelopmentConfig(Config):
    ENV = "development"
    DEVELOPMENT = True
    TESTING = True
    DEBUG = True
    SECRET_KEY = "test_environment_secret"