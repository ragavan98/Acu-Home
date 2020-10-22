# import datetime
# from sqlalchemy.orm import relationship
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import Integer, ForeignKey, String, Column
# from flask import Flask
# app = Flask(__name__)
# app.config.update({'SQLALCHEMY_DATABASE_URI': 'sqlite:///patients.sqlite'})
# db = SQLAlchemy(app)

# class roleTable(db.Model):
#     __tablename__ = 'roleTable'
#     roleId = db.Column(db.Integer, primary_key=True)
#     role = db.Column(db.String(40),unique=True,nullable=False)

# class healerTable(db.Model):
#     __tablename__ = 'healerTable'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40),nullable=False)
#     userId  = db.Column(db.String(15), unique=True, nullable=True)
#     emailId = db.Column(db.String(40),unique=True,nullable=False)
#     password = db.Column(db.String(20),unique=True,nullable=False)
#     mobile  = db.Column(db.String(20),nullable=True)
#     createdDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#     roleId = db.Column(db.Integer,db.ForeignKey('roleTable.roleId',ondelete='CASCADE'))
#     # role = relationship('roleTable',foreign_keys="roleTable.roleId")
    

# class patientTable(db.Model):
#     __tablename__ = 'patientTable'
#     patientId = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40), nullable=False)
#     userId  = db.Column(db.String(20), unique=True, nullable=True)
#     age  = db.Column(db.Integer,nullable=False)
#     gender  = db.Column(db.String(10),nullable=True)
#     city  = db.Column(db.String(20),nullable=True)
#     mobile  = db.Column(db.String(20),nullable=True)
#     operationUnderGone  = db.Column(db.String(30),nullable=True)
#     referredBy  = db.Column(db.String(30),nullable=True)
#     createdDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#     roleId = db.Column(db.Integer,db.ForeignKey('roleTable.roleId',ondelete='CASCADE'))
#     # role = relationship('roleTable',foreign_Keys="roleTable.roleId")

# class problemTable(db.Model):
#     __tablename__ = 'problemTable'
#     problemId = db.Column(db.Integer, primary_key=True)
#     problem = db.Column(db.String(40), nullable=False)
#     howLongSuffered = db.Column(db.String(30) ,nullable=False)
#     medicinesFollowed = db.Column(db.String(40), nullable=False)
#     acuPoints = db.Column(db.String(40),nullable=False)
#     foodSuggestion = db.Column(db.String(40), nullable=False)
#     howLongShouldVisit = db.Column(db.String(40), nullable=False)
#     attendedBy = db.Column(db.String(30), nullable=False)
#     createdDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#     # patient = relationship('patientTable')
#     patientId = db.Column(db.Integer,db.ForeignKey('patientTable.patientId',ondelete='CASCADE'))
    

# class feedbackTable(db.Model):
#     __tablename__ = 'FeedbackTable'
#     feedbackId = db.Column(db.Integer, primary_key=True)
#     feedback = db.Column(db.String(40), nullable=False)
#     createdDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#     # problem = relationship('problemTable')
#     problemId = db.Column(db.Integer,db.ForeignKey('problemTable.problemId',ondelete='CASCADE'))

# def init_db():
#     db.create_all()

# if __name__ == '__main__':
#     init_db()