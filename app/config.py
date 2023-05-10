import os

class Config:
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:6969/postgres')
    OUTPUT_FILES_DIR = os.environ.get('OUTPUT_FILES_DIR', '/Users/Chuz/Documents/Flask/first_attempt/output_files/')
    HISTORICAL_FILES_DIR = os.environ.get('HISTORICAL_FILES_DIR', '/Users/Chuz/Documents/Flask/first_attempt/historical_files/')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}