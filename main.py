from flask import Flask , render_template,session,redirect,url_for,flash
from flask import request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from flask_moment import Moment
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from threading import Thread

import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
cb = SQLAlchemy(app)
moment = Moment(app)
migrate = Migrate(app, db)
migrate = Migrate(app, cb)

app.config['SECRET_KEY'] = 'hard to guess'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[Question- Answer]'
app.config['FLASK_MAIL_SENDER'] = 'ADMIN <webdev.205120072@gmail.com>'
app.config['ADMIN'] = os.environ.get('ADMIN')

mail = Mail(app)

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)
def send_mail(to,subject,template,**kwargs):
    msg=Message(app.config['MAIL_SUBJECT_PREFIX']+subject,sender=app.config['FLASK_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr
    mail.send(msg)

class Question(db.Model):
    __tablename__='question'
    id = db.Column(db.Integer, primary_key =True)
    email = db.Column(db.String(64),unique=True,index=True)
    phone = db.Column(db.String(64) , unique=False , nullable = False)
    question = db.Column(db.String(200), unique=False, nullable=False)
   
    def __repr__(self):
         return f"Question('{self.email}' , '{self.phone}')"

class Answer(cb.Model):
    __tablename__='ans'
    id = cb.Column(cb.Integer, primary_key =True)
    abc = cb.Column(cb.String(300), unique=False , nullable=False)
    
    def __repr__(self):
        return f"Answer('{self.abc}')"


@app.route("/")
def index():
    return render_template("home.html")

@app.route("/Ask_Questions", methods=['GET' , 'POST'])
def ask_question():
    if request.method == "POST":
        Email = request.form.get("Email")
        Phone = request.form.get("Phone")
        ques = request.form.get("Question")
        u=Question(email=Email, phone=Phone, question=ques)
        db.session.add(u)
        db.session.commit()
        if app.config['ADMIN']:
            send_mail(app.config['ADMIN'],'New Question','mail/query',email=Email, phone=Phone, message=ques)
        flash('YOUR QUESTION  HAS BEEN PLACED SUCCESSFULLY !!!!',category='alert')
    return render_template("ask.html")

@app.route("/Questions")
def questions():
    #data=Question.query.filter_by(Question.question)
    data=Question.query.all()
    return render_template("ques.html",data=data)

@app.route("/Answers", methods=['GET','POST'])
def answer():
    if request.method == "POST":
        ty=request.form.get("xyz")
        a=Answer(abc=ty)
        cb.session.add(a)
        cb.session.commit()
        flash('YOUR ANSWER  HAS BEEN PLACED SUCCESSFULLY !!!!',category='alert')
    answ=Answer.query.all()
    return render_template("ans.html", d=answ)


@app.errorhandler(404)
def page_not_found(e):
        return render_template('404.html') , 404

@app.errorhandler(500)
def internal_server_error(e):
        return render_template('500.html') , 500

