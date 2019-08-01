import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'madisoncrimes-data', 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_DIR = os.path.join(basedir, 'madisoncrimes-data')
