from flask import Flask, request, redirect, url_for, render_template
from flask_modus import Modus
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://localhost/flask_one_to_many"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
modus = Modus(app)
db = SQLAlchemy(app)
Migrate(app, db)


class Student(db.Model):

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    excuses = db.relationship('Excuse', backref='student',
                                lazy='dynamic')
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

class Excuse(db.Model):
    __tablename__ = "excuses"

    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text)
    is_believable = db.Column(db.Text)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    




@app.route('/')
def root():
    return redirect(url_for('index'))


@app.route('/students', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        new_student = Student(request.form['first_name'],
                              request.form['last_name'])
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('students/index.html', students=Student.query.all())


@app.route('/students/new')
def new():
    return render_template('students/new.html')


@app.route('/students/<int:id>/edit')
def edit(id):
    return render_template('students/edit.html', student=Student.query.get(id))


@app.route('/students/<int:id>', methods=["GET", "PATCH"])
def show(id):
    found_student = Student.query.get(id)
    if request.method == b'PATCH':
        found_student.first_name = request.form['first_name']
        found_student.last_name = request.form['last_name']
        db.session.add(found_student)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('students/show.html', student=found_student)

@app.route("/students/<int:id>/excuses", methods = ["GET", "POST"])
def excuses_index(id):
    found_student = Student.query.get(id)
    if request.method == "POST":
        new_excuse = Excuse(content = request.form.get("content"), is_believable = request.form.get("is_believable"), student_id = id)
        db.session.add(new_excuse)
        db.session.commit()
        return redirect(url_for("excuses_index", id = id))

    
    excuses_list = found_student.excuses.all()
    return render_template("excuses/index.html", excuses=excuses_list, student= found_student)



@app.route("/students/<int:id>/excuses/new")
def new_excuse(id):

    return render_template("/excuses/new.html", id = id)


@app.route("/students/<int:id>/excuses/<int:excuse_id>/edit", methods = ["GET", "PATCH","DELETE"])
def edit_excuse(id,excuse_id):
    print(id)
    found_student = Student.query.get(id)
    found_excuse = Excuse.query.get(excuse_id)
    excuses_list = found_student.excuses.all()
    if request.method == b'DELETE':
        db.session.delete(found_excuse)
        db.session.commit()
        return redirect(url_for('excuses_index', id = found_student.id))
    elif request.method == b"PATCH":
 
        found_excuse.content = request.form.get("content")
        found_excuse.is_believable = request.form.get("is_believable")
       
        db.session.add(found_excuse)
        db.session.commit()

        return redirect(url_for("excuses_index", id = found_student.id))
        
        # return render_template("excuses/index.html",excuses = excuses_list, student = found_student)
    return render_template("excuses/edit.html",excuse = found_excuse, student = found_student)