import uuid
from flask import Flask,jsonify,send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask import request


from config import app_config

db = SQLAlchemy()
login_manager = LoginManager()
import os
from app.models import Experiments,ExperimentVersion
from shutil import make_archive
from werkzeug.utils import secure_filename
from sqlalchemy import desc

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    #app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)

    # temporary route
    @app.route('/')
    def hello_world():
        return 'Docker Test is up and running'

    @app.route( '/create-experiment',methods=['POST'])
    def create_experiment():
        if request.method == 'POST':
            reqData = request.json
            name = reqData['name']
            desc = reqData['desc']
            author = reqData['author']
            id = uuid.uuid4()
            if True:
                experiments = Experiments( uuid = id,name = name, desc = desc, author = author )
                db.session.add( experiments )
                db.session.commit()
                os.mkdir(app.config['EXPERIMENT_FILE_PATH']+str(id))
                return jsonify({'experiment_id':id})
        return jsonify({'error':'some error occured'})

    @app.route( '/add-experiment-data/<experiment_id>',methods=['POST'] )
    def add_experiment(experiment_id):
        if experiment_id:
            experiment = Experiments.query.filter_by( uuid=experiment_id ).first()
            db.session.commit()
            if experiment:
                count = ExperimentVersion.query.filter_by( experiment_uuid=experiment_id ).count()
                count =  int(count)
                folderName = experiment_id+'_'+str(count+1)
                folderNamePath=app.config['EXPERIMENT_FILE_PATH'] + experiment_id + '/'+folderName+'/'
                os.mkdir(folderNamePath)
                for file in ['label','weight']:
                    if file in request.files:
                        reqFile = request.files[file]
                        reqFile.save( os.path.join( folderNamePath, file ))

                zipFolderPath = app.config['EXPERIMENT_FILE_PATH'] + experiment_id + '/'+folderName+'_'+'data'

                make_archive(zipFolderPath,'zip',folderNamePath)
                experimentVersion = ExperimentVersion( experiment_uuid=experiment_id, version=count+1, file_path=zipFolderPath )
                db.session.add( experimentVersion )
                db.session.commit()

        return jsonify({'success':True})



    @app.route( '/get-experiment-data/<experiment_id>' ,methods=['GET'])
    def get_experiment_data(experiment_id):
        version = request.args.get('version', default = None, type = int)
        if version:
            version= int(version)
            expVersion = ExperimentVersion.query.filter_by(experiment_uuid = experiment_id).filter_by(version=version).first()
        else:
            expVersion = ExperimentVersion.query.filter_by(experiment_uuid = experiment_id).order_by(desc(version)).first()

        if expVersion:
            version = str(expVersion.version)
            path = experiment_id+'/'+experiment_id+'_'+version+'_data.zip'
            return send_file( '/Photos-Docker-Flask/'+app.config['EXPERIMENT_FILE_PATH']+path, as_attachment=False )
        return jsonify({'error':"invalid data provided"})


    login_manager.init_app(app)
    login_manager.login_message = 'You must be logged in to access this page'
    login_manager.login_view = 'auth.login'

    migrate = Migrate(app,db)

    from app import models

    return app
