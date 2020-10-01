from flask import Flask, render_template, request,session,redirect,flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import pymysql
pymysql.install_as_MySQLdb()
from werkzeug.utils import secure_filename
import json
import os
import math


with open('template/config.json','r') as file:
    params=json.load(file)['params']
app=Flask(__name__,template_folder='template')
app.secret_key='super secret key'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USERNAME=params['gmail-id'],
    MAIL_PASSWORD=params['gmail-password'],
    MAIL_USE_SSL=True,)
app.config['UPLOAD_FILE']=params['upload_location']
mail=Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
db = SQLAlchemy(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.String(120), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)



class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(120), nullable=False)
    sub_heading = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=False)


@app.route('/')
def home():
    posts=Post.query.filter_by().all()  #[0:int(params['no_of_post'])]
    last=math.ceil(len(posts)/int(params['no_of_post']))
    page=request.args.get('page')
    if (not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]
    if(page==1):
        prev="#"
        nex="/?page="+str(page+1)
    elif(page==last):
        prev="/?page="+str(page-1)
        nex="#"
    else:
        prev="/?page="+str(page-1)
        nex="/?page="+str(page+1)
            
    return render_template('index.html',params=params,posts=posts,nex=nex,prev=prev)


@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    posts=Post.query.filter_by().all()
    if 'username' in session and session['username']==params['user-id']:
        return render_template('dashboard.html',params=params,posts=posts)

    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username==params['user-id'] and password==params['user-pass']:
            session['username']=username
            return render_template('dashboard.html',params=params,posts=posts)


    return render_template('login.html',params=params)



@app.route('/about')
def about():
    return render_template('about.html',params=params)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/dashboard')

@app.route('/delete/<string:sno>')
def delete(sno):
    if 'username' in session and session['username']==params['user-id']:
        post=Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


    

# @app.route('/uploader', methods=['GET','POST'])
# def upload():
#     if 'username' in session and session['username']==params['user-id']:
#         if request.method=='POST':
#             f=request.files['file1']
#             f.save(os.path.join(app.config['UPLOAD_FILE'],secure_filename(f.filename)))
#             return "Uploaded Successfully"



@app.route('/post/<string:post_slug>',methods=['GET'])
def post(post_slug):
    post=Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post=post)

@app.route('/edit/<string:sno>',methods=['GET','POST'])
def edit(sno):
    
    if 'username' in session and session['username']==params['user-id']:
        
        if request.method=='POST':
            title=request.form.get('title')
            subheading=request.form.get('subheading')
            slug=request.form.get('slug')
            content=request.form.get('content')
            f=request.files['file2']
            imgfile=secure_filename(f.filename)
            imgfile='img/'+imgfile
            if sno=='0':
                post=Post(title=title,slug=slug,content=content,img_file=imgfile,sub_heading=subheading,date=datetime.now())
                db.session.add(post)
                db.session.commit()
                f.save(os.path.join(app.config['UPLOAD_FILE'],secure_filename(f.filename)))
                redirect('/dashboard')
            
            else:
                post=Post.query.filter_by(sno=sno).first()
                post.title=title
                post.sub_heading=subheading
                post.slug=slug
                post.content=content
                post.img_file=imgfile
                db.session.commit()
                redirect('/edit/'+sno)
        
        post=Post.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post,sno=sno)

@app.route('/contact', methods=['GET','POST'])
def contact():
    if (request.method =='POST'):
        flash("Your record has been submitted successfully we will get back to you as soon as possible.","success")
        name=request.form.get('name')
        phone=request.form.get('phone')
        message=request.form.get('message')
        email=request.form.get('email')
        entry=Contact(name=name,phone_number=phone,msg=message,date=datetime.now(),email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message("New Mail From "+name,
                            sender=email,
                            recipients=[params['gmail-id']],
                            body=message+"\n"+phone
                            )

    return render_template('contact.html',params=params)


app.run(debug=True)
