import os
from flask import Flask,session, flash, request, render_template, url_for, redirect,send_from_directory
from models import User, Product
from database import db_session
from database import init_db
from functools import wraps
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import math





app=Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#filetypes allowed
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.secret_key="Cindy Bosibori"

@app.before_request
def instantiatedb():
    #create database
    init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def index():
    return render_template('login.html')
    

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post_user',methods=['GET','POST'])
def post_user():
    if request.method == 'POST':
         user=User(request.form['uname'], request.form['phoneNumber'], request.form['email'], request.form['pwd'], request.form['dateofBirth'], request.form['height'], request.form['weight'], request.form['storedCash'])
         db_session.add(user)
         db_session.commit()
         flash('Successfully Registered!')
         return render_template('home.html')
    return render_template('post_user.html')
     


@app.route('/login',methods=['GET','POST'])
def login():
    error=None
    if request.method=='POST':
        email=request.form['email']
        pwd=request.form['pwd']

        user=User.query.filter_by(email=email).one()
        if user is not None and user.pwd == pwd:
            session['logged_in']=True
            session['username']=user.uname
            session['id']=user.id
            return render_template('home.html')

        else:
            flash('invalid login')
            return render_template('login.html')
      
    return render_template('login.html')


@app.route('/admin',methods=['GET','POST'])
def admin():
    error=None
    if request.method=='POST':
        users=User.query.all()
        email=request.form['email']
        pwd=request.form['pwd']

        for user in users:
            if pwd not in user.pwd and email not in user.email:
                flash('not valid admin')
                return render_template('admin.html')

            else:
                username=user.uname
                session['logged_in']=True
                session['username']=username
                return redirect(url_for('admindashboard'))
      
    return render_template('admin.html')

#check login status

def is_loggedin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap
def is_adminlogin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('admin'))
    return wrap

@app.route('/logout')
@is_loggedin
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/adminlogout')
@is_adminlogin
def adminogout():
    session.clear()
    return redirect(url_for('admin'))


#admin dashboard
@app.route('/admindashboard')
@is_adminlogin
def admindashboard():
    return render_template('admindashboard.html')

@app.route('/userdashboard', methods=['GET', 'POST'])
@is_adminlogin
def userdashboard():
    users=User.query.all()
    return render_template('userdashboard.html', users=users)

#edit all users -->admin function

@app.route('/edit_users/<string:id>',methods=['GET','POST'])
@is_adminlogin
def edit_users(id):
    user=User.query.filter_by(id=id).one()
    #
    if request.method=='POST':
        user.uname= request.form['uname']
        user.phoneNumber=request.form['phoneNumber']
        user.email=request.form['email']
        user.pwd=request.form['pwd']
        user.dateofBirth=request.form['dateofBirth']
        user.height=request.form['height']
        user.weight=request.form['weight']
        user.storedCash=request.form['storedCash']
        #db_session.add(user)
        db_session.commit()
        return redirect(url_for('admindashboard'))
      
    return render_template('edit_users.html',  user=user)

@app.route('/uedit/<string:uid>', methods=['GET','POST'])
@is_loggedin
def prof(uid):
    user= User.query.filter_by(id=uid).one()
    return render_template('uedit.html', user=user)

#user edits own profile-
@app.route('/changeprofdtls/<string:id>',methods=['GET','POST'])
@is_adminlogin
def edit_prof(id):
    user=User.query.filter_by(id=id).one()
    #
    if request.method=='POST':
        user.uname= request.form['uname']
        user.phoneNumber=request.form['phoneNumber']
        user.email=request.form['email']
        user.pwd=request.form['pwd']
        user.dateofBirth=request.form['dateofBirth']
        user.height=request.form['height']
        user.weight=request.form['weight']
        user.storedCash=request.form['storedCash']
        #db_session.add(user)
        db_session.commit()
        return redirect(url_for('login'))
      
    return render_template('changeprofdtls.html',  user=user)


@app.route('/send_result/<filename>')
@is_loggedin
def send_result(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/productview')
def gallery():
    error=None
    image_names=os.listdir('./images')
    #imagedetails=Product.query.all()
    #dbimgname=imagedetails.productImage
    #if not None and image_names in dbimage:
    return render_template('productview.html', image_names=image_names)
    #else:
        #error='image does not exist in our database'


    ##return render_template('productview.html', prod=prod)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/addproduct',methods=['GET','POST'])
@is_adminlogin
def addproduct():
     if not session.get('logged_in'):
        abort(401)
     if request.method == 'POST':
         file = request.files['pimage']
         #if file and allowed_file(file.filename):
         filename = secure_filename(file.filename)
         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
         #post=Product(request.form['pname'], filename,request.form['cost'])
         #db_session.add(post)
         #@db_session.commit()
        #return redirect(url_for('addproduct', filename=filename))
     return render_template('addproduct.html')
#admin delete user
@app.route('/delete/<string:id>', methods=['GET','POST'])
@is_adminlogin
def delete(id):
    user=User.query.filter_by(id=id).one()
    db_session.delete(user)
    db_session.commit()

    return  redirect(url_for('admindashboard'))


#fetch users
@app.route('/dashboard')
def dashbaord():
    p=User.query.all()
    print(p)

    return render_template('dashboard.html')

@app.route('/showStats')
@is_adminlogin
def stats():
    b=User.query.all()
    return render_template('showStats.html')



    



if __name__=='__main__':
    app.run(debug=True)


