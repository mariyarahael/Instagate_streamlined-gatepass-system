import os
from flask import Flask
from flask_restful import Api
from models.models import db
from flask_mail import Mail, Message

app = None


def start_app():
    app=Flask(__name__,template_folder="templates")
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///gatepassdb.sqlite3"
    app.config['SECRET_KEY'] = os.urandom(24).hex()
    db.init_app(app)
    app.app_context().push()
    app.debug = True
    return app


app=start_app()
api = Api(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gatepassportal75@gmail.com'  # Change this
app.config['MAIL_PASSWORD'] = 'rsul oxpn wcbv wljo'  # Change this
app.config['MAIL_DEFAULT_SENDER'] = 'gatepassportal75@gmail.com'

mail = Mail(app)

from controllers.controllers import *
from controllers.resources import *

api.add_resource(StudentLoginAPI, "/api/login")
api.add_resource(DownloadGatePassAPI, "/api/download-gatepass/<int:student_id>")

if __name__=="__main__":
    app.run()
