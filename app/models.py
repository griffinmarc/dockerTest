from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Experiments(UserMixin, db.Model):
    """
    Create an experiments table
    """
    __tablename__ = 'experiments'

    uuid = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(20))
    desc = db.Column(db.String(200))
    author = db.Column(db.String(20))



class ExperimentVersion(db.Model):
    """
    Create a experiment_versions table
    """

    __tablename__ = 'experiment_versions'

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    experiment_uuid = db.Column( db.String(100))
    version = db.Column( db.Integer )
    config  = db.Column( db.String(255) )
    file_path = db.Column( db.String(200) )