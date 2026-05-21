from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

# User Model
class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )
    tasks = db.relationship(
    'Task',
    backref='owner',
    lazy=True
)

# Database Model
class Task(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    completed = db.Column(
        db.Boolean,
        default=False
    )
    user_id = db.Column(
    db.Integer,
    db.ForeignKey('user.id'),
    nullable=False
)
@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))
# Home Route
@app.route("/", methods=["GET", "POST"])
@login_required
def home():

    # Add Task
    if request.method == "POST":

        task_title = request.form["title"]

        new_task = Task(
    title=task_title,
    user_id=current_user.id
)

        db.session.add(new_task)

        db.session.commit()

        return redirect("/")

    # Show Tasks
    tasks = Task.query.filter_by(
    user_id=current_user.id
).all()

    return render_template(
        "index.html",
        tasks=tasks
    )

# Run App
# Delete Task
@app.route("/delete/<int:id>")
def delete(id):

    task = Task.query.filter_by(
    id=id,
    user_id=current_user.id
).first_or_404()

    db.session.delete(task)

    db.session.commit()

    return redirect("/")
# Complete Task
@app.route("/complete/<int:id>")
# Complete Task
@app.route("/complete/<int:id>")
def complete(id):

    task = Task.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    task.completed = not task.completed

    db.session.commit()

    return redirect("/")
# Edit Task
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    task = Task.query.filter_by(
    id=id,
    user_id=current_user.id
).first_or_404()

    if request.method == "POST":

        task.title = request.form["title"]

        db.session.commit()

        return redirect("/")

    return render_template(
        "edit.html",
        task=task
    )
# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        password = generate_password_hash(
            request.form["password"]
        )

        user = User(
            username=username,
            password=password
        )

        db.session.add(user)

        db.session.commit()

        return redirect("/login")

    return render_template("register.html")
# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect("/")

    return render_template("login.html")

# Logout
@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/login")
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)