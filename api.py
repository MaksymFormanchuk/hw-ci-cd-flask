from asyncio.proactor_events import _ProactorBasePipeTransport
import json
import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from marshmallow import Schema, fields

dotenv.load_dotenv()

db_user = os.environ.get('DB_USERNAME')
db_pass = os.environ.get('DB_PASSWORD')
db_hostname = os.environ.get('DB_HOSTNAME')
db_name = os.environ.get('DB_NAME')

DB_URI = 'mysql+pymysql://{db_username}:{db_password}@{db_host}/{database}'.format(db_username=db_user, db_password=db_pass, db_host=db_hostname, database=db_name)

engine = create_engine(DB_URI, echo=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(13), unique=True, nullable=False)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class StudentSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()

student_schema = StudentSchema

@app.route('/', methods = ['GET'])
def home():
    return '<p>Hello from students API!</p>', 200

@app.route('/api', methods = ['GET'])
def api_main():
    with open('main.json', 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
    return jsonify(json_data), 200

@app.route('/api/students', methods=['GET'])
def get_all_students():
    students = Student.get_all()
    student_list = StudentSchema(many=True)
    response = student_list.dump(students)
    return jsonify(response), 200

@app.route('/api/students/get/<int:id>', methods = ['GET'])
def get_student(id):
    student_info = Student.get_by_id(id)
    serializer = StudentSchema()
    response = serializer.dump(student_info)
    return jsonify(response), 200

@app.route('/api/students/add', methods = ['POST'])
def add_student():
    json_data = request.get_json()
    new_student = Student(
        name= json_data.get('name'),
        email=json_data.get('email'),
        age=json_data.get('age'),
        cellphone=json_data.get('cellphone')
    )
    new_student.save()
    serializer = StudentSchema()
    data = serializer.dump(new_student)
    return jsonify(data), 201

@app.route('/api/students/modify/<int:id>', methods=['PATCH'])              # adding modify endpoint
def modify_stud_data(id):
    ch_data = Student.get_by_id(id)
    req_data = request.get_json()
    if req_data.get('name'):
        ch_data.name = req_data.get('name')
    if req_data.get('email'):
        ch_data.email = req_data.get('email')
    if req_data.get('age'):
        ch_data.age = req_data.get('age')
    if req_data.get('cellphone'):
        ch_data.cellphone = req_data.get('cellphone') 
    ch_data.save()
    serializer = StudentSchema()
    changed = serializer.dump(ch_data)
    return jsonify(changed), 200

@app.route('/api/students/change/<int:id>', methods=['PUT'])                # adding change endpoint
def change_stud_data(id):
    ch_data = Student.get_by_id(id)
    req_data = request.get_json()
    new_data = Student(
        name = req_data.get('name'),
        email = req_data.get('email'),
        age = req_data.get('age'),
        cellphone = req_data.get('cellphone')
    )
    ch_data.name = new_data.name
    ch_data.email = new_data.email
    ch_data.age = new_data.age
    ch_data.cellphone = new_data.cellphone

    ch_data.save()
    serializer = StudentSchema()
    changed = serializer.dump(ch_data)
    return jsonify(changed), 201

@app.route('/api/deleteStudent/<int:id>', methods=['DELETE'])               # adding delete endpoint
def del_student(id):
    ch_data = Student.get_by_id(id)
    ch_data.delete()
    serializer = StudentSchema()
    changed = serializer.dump(ch_data)
    return jsonify(changed), 201

@app.route('/api/heath-check/ok', methods=['GET'])                          # checking health - Ok status
def healthcheck_ok():
    return jsonify('Status: OK'), 200

@app.route('/api/heath-check/bad', methods=['GET'])                         # checking health - Error status
def healthcheck_bad():
    return jsonify('Status: Error'), 500

if __name__ == '__main__':
    if not database_exists(engine.url):
        create_database(engine.url)
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
