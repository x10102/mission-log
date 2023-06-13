# External
from flask import Flask, redirect, url_for, render_template, request

# Internal
from core import db
from passwords import pw_hash, pw_verify
from users import User, UserRole

# Builtins
from sys import argv
from os import remove

app = Flask(__name__)

@app.route('/')
def index():
    page = request.args.get("page", type=int, default=0)
    entries = db.get_frontpage(page)
    return render_template('index.j2', entries=entries)

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
                
    app.run(debug=True, host="0.0.0.0")