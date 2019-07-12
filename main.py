from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy

app= Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO']=True
db= SQLAlchemy(app)
app.secret_key= 'YakshaWiKlOSSja'

class Blog(db.Model):

    id= db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(255))
    body= db.Column(db.String(255))

    def __init__(self, title, body):
        self.title= title
        self.body= body

@app.route('/blog', methods=['POST', 'GET'])
def blog():

        blog_id=request.args.get('id')

        if blog_id:
            inv_blog= Blog.query.get(blog_id)
            return render_template('individual.html', inv_blog=inv_blog)
        else:    
            blogs= Blog.query.all()
            return render_template('blog.html', blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method=='POST':

        title= request.form['title']
        body= request.form['body']
        
        title_error=''
        body_error=''

        new_entry=Blog(title, body)
      

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

if __name__=='__main__':
    app.run()
