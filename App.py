# External
from flask import Flask, redirect, url_for, render_template, request, abort, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from waitress import serve

# Internal
from core import db
from passwords import pw_hash, pw_verify
from users import User, UserRole
from forms import *
from entries import Entry
from markup import parse_comment_string
from secrets import token_bytes

# Builtins
from sys import argv
from os import remove, environ as env
import json

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@app.errorhandler(404)
def e404(e):
    return render_template('error.j2', code=404, message='Not Found')

@app.errorhandler(403)
def e403(e):
    return render_template('error.j2', code=403, message='Forbidden')

@app.errorhandler(405)
def e405(e):
    return render_template('error.j2', code=405, message='Method Not Allowed')

@app.errorhandler(500)
def e500(e):
    return render_template('error.j2', code=500, message='Internal Server Error')

def add_globals():
    return {"user": app.config['MAIN_USER'], "title": app.config['PAGE_TITLE']}

@login_manager.user_loader
def load_user(uid: str):
    return db.get_user(int(uid))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        form = LoginForm()
        if form.validate_on_submit():
            user = db.get_username(form.login.data)
            if not user:
                flash('Username invalid')
                return redirect(url_for('login'))
            if not pw_verify(form.password.data, user.password):
                flash('Password invalid')
                return redirect(url_for('login'))
            login_user(user)
            flash("Logged in")
            return redirect(request.args.get('next', type=str, default=None) or url_for('index'))
    return render_template('login.j2', form=LoginForm())

@app.route('/')
def index():
    page = request.args.get("page", type=int, default=0)
    entries = db.get_frontpage(page, private=not current_user.is_anonymous)
    return render_template('index.j2', entries=entries)

@app.route('/entry/create', methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        form = EntryCreateForm()
        if form.validate_on_submit():
            e = Entry(parse_comment_string(form.text.data), current_user, form.private.data)
            eid = db.create_entry(e)
            return redirect(url_for('view_entry', eid=eid))
    return render_template('create.j2', form=EntryCreateForm())

@app.route('/entry/<int:eid>')
def view_entry(eid: int):
    ent = db.get_entry(eid)
    if not ent:
        abort(404)
    else:
        return render_template('entry.j2', entry=ent, is_author=current_user==ent.author)
    
@app.route('/entry/<int:eid>/delete', methods=["POST"])
def delete_entry(eid: int):
    e = db.get_entry(eid)
    if not e:
        abort(404)
    if not e.author == current_user:
        abort(403)
    db.delete_entry(eid)
    return redirect(url_for('index'))

if __name__ == "__main__":
    if len(argv) > 1:
        match argv[1]:
            case "init":
                print("Adding initial user...")
                try: 
                    user = input("Username: ")
                    password = pw_hash(input("Password: "))
                    u = User(login=user, password=password, role=UserRole.OWNER)
                    db.create_user(u)
                    print(f"User {user} created succesfully")
                    exit(0)
                except EOFError:
                    print("Aborted.")
                    exit(-1)
            case "drop":
                remove('data/diary.db')
                db.close()
                exit(0)
    
    if env.get('INIT_USER'):
        user = env.get('INIT_USER')
        password = env.get('INIT_PASSWORD')
        u = User(login=user, password=pw_hash(password), role=UserRole.OWNER)
        db.create_default_user(u)

    app.config.from_file('config.json', load=json.load)
    app.context_processor(add_globals)
    app.add_template_global(current_user, 'current_user')
    app.add_template_global('base.j2', 'current_base')
    if not app.config['SECRET_KEY']:
        app.config['SECRET_KEY'] = token_bytes(24)
    if app.config['FLASK_DEBUG']:
        app.run(host="0.0.0.0")
    else:
        serve(app, port=8080)