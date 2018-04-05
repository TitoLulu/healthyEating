import os
from flask import Flask,session, jsonify,flash, request, render_template, url_for, redirect,send_from_directory
from models import User, Product, Utrack, Delivery
from database import db_session
from database import init_db
from functools import wraps
from werkzeug.utils import secure_filename
import pygal
import os, sys
import statistics
import simplejson as json





UPLOAD_FOLDER = r'static/images'


#filetypes allowed
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app=Flask(__name__)




app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['WHOOSH_BASE']='whoosh'



app.secret_key="Cindy Bosibori"

'''
instantiate the database
'''

@app.before_request
def instantiatedb():
    #create database
    init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

'''
direct user to login page
'''
@app.route('/')
def index():
    return render_template('home.html')
    
'''
about the company
'''
@app.route('/about')
def about():
    return render_template('about.html')
'''
registers new user and directs to login
access to website for new user happens after login
'''
@app.route('/post_user',methods=['GET','POST'])
def post_user():
    if request.method == 'POST':
         user=User(request.form['uname'], request.form['phoneNumber'], request.form['email'], request.form['pwd'],request.form['storedCash'])
         db_session.add(user)
         db_session.commit()
         flash('Successfully Registered!')
         return render_template('login.html')
    return render_template('post_user.html')

'''
login for registered users
'''
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        error = ""
        email=request.form['email']
        pwd=request.form['pwd']
        if pwd and email:
            user=User.query.filter_by(email=email).one()
            if user is not None and user.pwd == pwd:
                session['logged_in']=True
                session['username']=user.uname
                session['id']=user.id
                return render_template('home.html')
            else:
                error="Invalid email and password"
                return render_template('login.html')

    return render_template('login.html')



'''
admin login
'''
@app.route('/admin',methods=['GET','POST'])
def admin():
    error=None
    if request.method=='POST':
        email=request.form['email']
        pwd=request.form['pwd']

        user=User.query.filter_by(email=email).one()
        if user is None and user.pwd !=pwd:
            flash('not valid admin')
            return render_template('admin.html')
    
        else:
            username=user.uname
            session['logged_in']=True
            session['username']=username
            flash('login successful')
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
#check login status for admin
def is_adminlogin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('admin'))
    return wrap
#user sessiom
@app.route('/logout')
#@is_loggedin
def logout():
    session.clear()
    return render_template('home.html')
    
#admin session
@app.route('/adminlogout')
@is_adminlogin
def adminogout():
    session.clear()
    return redirect(url_for('admin'))

@app.route('/trackuser/<string:id>', methods=['GET','POST'])
@is_loggedin
def hweight(id):
    user=User.query.filter_by(id=id).one()
    if request.method=='POST':
        uhw=Utrack(uid=user.id, height=request.form['height'], weight=request.form['weight'], datechanged=request.form['date'])
        db_session.add(uhw)
        db_session.commit()


    return render_template('trackuser.html', user=user)



#admin dashboard
@app.route('/admindashboard')
@is_adminlogin
def admindashboard():
    return render_template('admindashboard.html')
#returns list of all users
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
@is_loggedin
def edit_prof(id):
    user=User.query.filter_by(id=id).one()
    
    #update user details
    if request.method=='POST':
        
    
        user.uname= request.form['uname']
        user.phoneNumber=request.form['phoneNumber']
        user.email=request.form['email']
        user.pwd=request.form['pwd']
        user.storedCash=request.form['storedCash']
        db_session.commit()
        
        #flash('update successful, login to access page')
        return redirect(url_for('logout'))
      
    return render_template('changeprofdtls.html',  user=user)


@app.route('/send_result/<filename>')
@is_loggedin
def send_result(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
#displays images using their relative path
@app.route('/productview')
@is_loggedin
def gallery():
    error=None
    
    image_names=Product.query.all()
  
    return render_template('productview.html', image_names=image_names)
#home view
@app.route('/home')
#@is_loggedin
def hview():
    error=None
    
    image_names=Product.query.all()
  
    return render_template('home.html', image_names=image_names)


@app.route('/singleProductView/<int:id>', methods=['GET'])
@is_loggedin
def foodImage(id):
    #view for a single product
    image_view=Product.query.filter_by(id=id).one()
    

    return render_template('singleProductView.html', image_view=image_view)

@app.route('/delivery/<string:id>', methods=['GET','POST'])
@is_loggedin
def delivery(id):
    prod=Product.query.filter_by(id=id).one()
   
    #user=User.query.filter_by(id=session['id']).one()
    

    select=request.form.get('delivery')
    

    
    if request.method=='POST':
        udelivery=Delivery(prod.id, prod.productname, select)
        db_session.add(udelivery)
        db_session.commit()

    return render_template('delivery.html')



@app.route('/editSubscription/<string:id>')
@is_loggedin
def esub(id):
    #directs user to edit subscription.
    sub=Delivery.query.filter_by(did=id).all()

    return render_template('editSubscription.html', sub=sub)

@app.route('/cancelsub/<string:id>')
@is_loggedin
def csub(id):
    #cancel subscription, redirect client to products page
    deleteSub=Delivery.query.filter_by(did=id).first()
    db_session.delete(deleteSub)
    db_session.commit()

    return render_template('productview.html')


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
         if file and allowed_file(file.filename):
             filename = secure_filename(file.filename)
             dbpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
             file.save(dbpath)
             post=Product(request.form['pname'],dbpath,request.form['cost'])
             db_session.add(post)
             db_session.commit()
             flash('product added Successfully')
             '''
             return redirect(url_for('addproduct', filename=filename))'''
     return render_template('addproduct.html')
#admin delete user
@app.route('/delete/<string:id>', methods=['GET','POST'])
@is_adminlogin
def delete(id):
    user=User.query.filter_by(id=id).one()
    db_session.delete(user)
    db_session.commit()

    return  redirect(url_for('admindashboard'))


#heigth and weight graphs 
@app.route('/dashboard/<string:id>')
@is_loggedin
def dashbaord(id):
 
    grph= User.query.filter_by(id=id).one()
    u=Utrack.query.filter_by(uid=id).all()
    print(u)

    heights, weights, dates = [], [], []
    
    for ut in u:
        heights.append(ut.height)
        weights.append(ut.weight)
        dates.append(ut.datechanged)

    graph=pygal.Line()
    graph.title='Change in height and weight over time'
    graph.x_lables= map(int,dates)
    graph.add('Height over time', heights)
    graph.add('Weight over time', weights)
    graph_data=graph.render_data_uri()
    
    
    return render_template('dashboard.html', graph_data=graph_data)



@app.route('/showStats')
@is_adminlogin
def stats():
    #shows the mean of heights and weights over time
    b=Utrack.query.all()
    heights, weights,dates=[],[],[]

    for ahw in b:
        #dates.append(ahw.datechanged)
        heights.append(ahw.height)
        weights.append(ahw.weight)

    graph=pygal.Bar()
    graph.title='Mean Height and Weight'
    graph.x_lables=map(str, '2018') 
    graph.add('Mean Height', statistics.mean(heights))
    graph.add('Mean Weight', statistics.mean(weights))
    graph_data=graph.render_data_uri()
    

    return render_template('showStats.html',graph_data=graph_data)


@app.route('/allStats')
@is_adminlogin
def allstats():
    search=request.args.get('search')
    b=Utrack.query.filter_by(uid=search).all()

    heights, weights,dates=[],[],[]

    for ahw in b:
        dates.append(ahw.datechanged)
        heights.append(ahw.height)
        weights.append(ahw.weight)

    graph=pygal.Line()
    graph.title='Height and Weight'
    graph.x_lables=dates 
    graph.add('Height', heights)
    graph.add('Weight', weights)
    graph_data=graph.render_data_uri()
    

    return render_template('allStats.html',graph_data=graph_data)



@app.route('/upcomingdeliveries')
@is_adminlogin
def updeliveries():
    #check upcoming deliveries
    alldeliveries=Delivery.query.all()


    return render_template('upcomingdeliveries.html', alldeliveries=alldeliveries)

#admin mark delivery as complete
@app.route('/cleardelivery/<string:id>', methods=['GET','POST'])
@is_adminlogin
def cdelivery(id):
    cdelivery=Delivery.query.filter_by(id=id).one()
    db_session.delete(cdelivery)
    db_session.commit()

    return  redirect(url_for('admindashboard'))



if __name__=='__main__':
    app.run(debug=True)


