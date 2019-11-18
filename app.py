from flask import Flask, render_template, url_for, request, flash, redirect
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_migrate import Migrate

import re

app = Flask(__name__)

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config["SECRET_KEY"] = "here is my secret key"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
login_manager = LoginManager(app)
moment = Moment(app)


migrate = Migrate(app, db)


class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(20), nullable=False, unique=True)
  email = db.Column(db.String(50), nullable=False, unique=True)
  password = db.Column(db.String(255), nullable=False)
  img_url = db.Column(db.String(155))

  def generate_password(self,password):
    self.password = generate_password_hash(password)

  def check_password(self,password):
    return check_password_hash(self.password,password)

class Post(db.Model):
  __tablename__ = 'posts'
  id = db.Column(db.Integer, primary_key=True)
  body = db.Column(db.String, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  like = db.Column(db.Integer, default=0)
  img = db.Column(db.String)
  created_at = db.Column(db.DateTime, server_default=db.func.now()) 
  updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
  view_count = db.Column(db.Integer, default=0)

class Comments(db.Model):
  __tablename__ = 'comments'
  id = db.Column(db.Integer, primary_key=True)
  body = db.Column(db.String, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  post_id = db.Column(db.Integer, nullable=False)
  created_at = db.Column(db.DateTime, server_default=db.func.now()) 
  updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

class PostLike(db.Model):
  __tablename__ = 'post_like'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer)
  post_id = db.Column(db.Integer)
    
db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route("/home")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('register'))
    posts = Post.query.order_by(Post.created_at.desc()).all()
    for post in posts:
        post.user = User.query.get(post.user_id)
        post.comments = Comments.query.filter_by(post_id=post.id).all()
        post.likes = PostLike.query.filter_by(post_id=post.id).all()
        for comment in post.comments:
            comment.user_name = User.query.get(comment.user_id)
        for like in post.likes:
            like.num = User.query.get(like.post_id)
    return render_template('home.html', posts=posts)


@app.route('/posts/top/')
def view_top_posts():

    posts = Post.query.order_by(Post.view_count.desc()).all()
    for post in posts:
        post.user = User.query.get(post.user_id)
        post.comments = Comments.query.filter_by(post_id=post.id).all()
        post.likes = PostLike.query.filter_by(post_id=post.id).all()
        for comment in post.comments:
            comment.user_name = User.query.get(comment.user_id)
        for like in post.likes:
            like.num = User.query.get(like.post_id)
    return render_template('home.html', posts=posts)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("register"))

@app.route("/profile", methods=["GET", "POST"])
def login():
    user = User.query.filter_by(email=request.form["email"]).first()
    if user and check_password_hash(user.password, request.form["password"]):
        login_user(user)
        return redirect(url_for('home'))
    else:
        flash("Login failed. Please check email and password", "danger")
        return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == "POST":
        check_email = User.query.filter_by(email=request.form['email']).first() 
        if check_email:  
            flash('Email already taken', 'warning') 
            return redirect(url_for('register')) 
        user = User(name=request.form["first_name"] +' '+ request.form["last_name"], email=request.form["email"], password=generate_password_hash(request.form["password"]))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/post/new', methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        if re.findall(r'(https?://[^\s]+)', request.form['post']):
            pattern = re.sub(re.findall(r'(https?://[^\s]+)', request.form['post'])[0], "", request.form['post'])
            post = Post(user_id=current_user.id, body=pattern, img=re.findall(r'(https?://[^\s]+)', request.form['post'])[0])
            db.session.add(post)
            db.session.commit()
        else:
            post = Post(user_id=current_user.id, body=request.form['post'])
            db.session.add(post)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('home.html', posts=posts)


@app.route('/profile/<id>', methods=["GET", "POST"])
def user_profile(id):
    posts = Post.query.filter_by(user_id=id).all()
    for post in posts:
        user = User.query.get(post.user_id)
        post.user_name = user.name
        post.user = User.query.get(post.user_id)
        comments = Comments.query.filter_by(post_id=post.id).all()
        post.comments = Comments.query.filter_by(post_id=post.id).all()
        for comment in post.comments:
            comment.user_name = User.query.get(comment.user_id)
    return render_template('user_profile.html', posts=posts, comments=comments)

@app.route('/view_post/<id>', methods=["GET", "POST"])
def view_post(id):
    post = Post.query.get(id)
    post.view_count = post.view_count + 1
    db.session.add(post)
    db.session.commit()
    comments = Comments.query.filter_by(post_id=post.id).all()
    posts = Post.query.order_by(Post.created_at.desc()).all()

    for post in posts:
        post.user = User.query.get(post.user_id)
        post.comments = Comments.query.filter_by(post_id=post.id).all()
        for comment in post.comments:
            comment.user_name = User.query.get(comment.user_id)
    post = Post.query.get(id)
    return render_template('view_post.html', post=post, posts=posts, comments=comments)





@app.route('/delete_post/<id>', methods=["GET", "POST"])
def delete_post(id):
    if request.method == "POST":
        post = Post.query.filter_by(id=id).first()
        print(post.user_id, current_user.id)
        if current_user.id == post.user_id:
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash("You cant delete this", "warning")
            return redirect(url_for('home'))
    return render_template('home.html')

@app.route("/post/<id>/comments", methods=["GET", "POST"])
@login_required
def comment(id):
    if request.method == "POST":
        comment = Comments(user_id=current_user.id, body=request.form['body'], post_id=id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('home.html')

@app.route('/post/comment/<id>', methods=["GET", 'POST'])
@login_required
def delete_comment(id):
    if request.method == "POST":
        comment = Comments.query.filter_by(id=id).first()
        if comment.user_id == current_user.id:
            db.session.delete(comment)
            db.session.commit()
            return redirect(url_for("home"))
        else:
            flash("You cant delete this post", "warning")
            return redirect(url_for('home'))
    return render_template("home.html")

@app.route('/edit_post/<id>', methods=["GET", "POST"])
@login_required
def edit_post(id):
    if request.method == "POST":
        post = Post.query.filter_by(id=id).first()
        post.body = request.form['body']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("home.html")

@app.route('/post/edit_comment/<id>', methods=["GET", "POST"])
@login_required
def edit_comment(id):
    if request.method == "POST":
        comment = Comments.query.filter_by(id=id).first()
        comment.body = request.form["body"]
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("home.html")


@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        user = User.query.get(current_user.id)
        user.img_url = request.form['url']
        db.session.commit()
    return render_template("account.html")

@app.route('/post/<id>/like', methods=["GET", "POST"])
def like(id):
    if request.method == "POST":
        if PostLike.query.filter_by(user_id=current_user.id, post_id=id).first():
            user = Post.query.filter_by(id=id).first()
            like = PostLike.query.filter_by(user_id=current_user.id, post_id=id).first()
            user = Post.query.filter_by(id=id).first()
            user.like = user.like - 1
            db.session.delete(like)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            like = PostLike(user_id=current_user.id, post_id=id)
            db.session.add(like)
            db.session.commit()
            user = Post.query.filter_by(id=id).first()
            user.like = user.like + 1
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug = True)


    