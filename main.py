from flask import Flask, request, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app= Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO']=True
db= SQLAlchemy(app)
app.secret_key= 'YakshaWiKlOSSjaXZyjeanmcaed'

class Blog(db.Model):

    id= db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(255))
    body= db.Column(db.String(255))
    owner_id= db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title= title
        self.body= body
        self.owner= owner

class User(db.Model):

    id= db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(255), unique=True)
    password= db.Column(db.String(255))
    blogs= db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username= username
        self.password= password 

@app.before_request
def required_login():
    allowed_routes= ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def blog():

    if session:
        owner= User.query.filter_by(username= session['username']).first()

    if "id" in request.args:
        post_id= request.args.get('id')
        blogs= Blog.query.filter_by(id= post_id).all()
        return render_template('blog.html', blogs= blogs, post_id= post_id)

    elif "user" in request.args:
        user_id= request.args.get('user')
        blogs= Blog.query.filter_by(owner_id= user_id).all()
        return render_template('blog.html', blogs= blogs)

    else:
        blogs= Blog.query.order_by(Blog.id.desc()).all()
        return render_template('blog.html', blogs= blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method=='POST':

        owner= User.query.filter_by(username=session['username']).first()
        title= request.form['title']
        body= request.form['body']
        
        title_error=''
        body_error=''

        new_entry=Blog(title, body, owner)
      

        if not body:
            body_error='Please enter the blog entry'
            body=''
        if not title:
            title_error='Please enter the title entry'
            title=''
        
        if title and body:
            db.session.add(new_entry)
            db.session.commit()
            new_entry= "/blog?id=" + str(new_entry.id)
            return redirect(new_entry)

        else:
            return render_template('newpost.html', title_error=title_error, body_error=body_error, body=body, title=title)
    else:
        return render_template('newpost.html')

@app.route('/signup', methods = ['POST', 'GET'])
def signup():

    user_error=''
    pass_error=''
    verify_error=''

    if request.method == 'POST':

        username= request.form['username']
        password= request.form['password']
        verify= request.form['verify']

        for char in username:
            if char==' ':
                user_error='Not a valid username'
                username=''
    
        if len(username)<3 or len(username)>20:
            user_error='Not a valid username'
            username=''
    
        if password==' ' or len(password)<3 or len(password)>20:
            pass_error='Not a valid password'
            password=''
    
        if verify==' ' or len(verify)<3 or len(verify)>20:
            verify_error='Not a valid password'
            verify=''

        if not username:

            user_error='Please enter a correct username'
            username=''

        if not password:

            pass_error='Please enter a valid password'
            password=''

        if not verify:

            verify_error='Please enter the same password'
            verify=''

        if password != verify:

            pass_error='Passwords do not match'
            verify_error='Passwords do not match'
            password=''
            verify=''

        existing_user= User.query.filter_by(username=username).first()
        if not user_error and not pass_error and not verify_error:
            if not existing_user:
                new_user= User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username']= username
                return redirect('/index')
            else:
                return redirect('/signup')
        else:
            return render_template('signup.html', pass_error= pass_error, 
                verify_error= verify_error, user_error= user_error, 
                username= username, password= password, verify= verify)

    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():

    username= ''
    user_error= ''
    pass_error= ''

    if request.method== 'POST':
        username= request.form['username']
        password= request.form['password']
        user= User.query.filter_by(username=username).first()
        
        if not username:
            user_error = "User not found."

        if username== ' ':
            user_error = "Enter your username."

        if password== ' ':
            pass_error = "Enter your password."

        if user and user.password != password:
            pass_error = "Invailid combination. Try again."
        
        if user and user.password== password:
            session['username']= username
            flash("logged in")
            
            return redirect('/newpost')
            
    return render_template('login.html', username=username, user_error=user_error, pass_error=pass_error)

@app.route('/logout')
def logout():
    
    del session['username']
    return redirect('/login')

@app.route('/index')
def index():

    users= User.query.all()
    return render_template('index.html', users=users)

if __name__=='__main__':
    app.run()
