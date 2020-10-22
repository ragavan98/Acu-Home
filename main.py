# from models.dbmodels import db, roleTable, patientTable, healerTable, problemTable, feedbackTable
import webbrowser
from threading import Timer
from json import JSONEncoder
from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask import g, render_template, request, jsonify, make_response, session, redirect, url_for
from flask_cors import CORS
import datetime
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, ForeignKey, String, Column
import sys
import xlsxwriter
from flask import send_file
import pandas as pd
import xlrd
app = Flask(__name__)


db = SQLAlchemy(app)


class roleTable(db.Model):
    __tablename__ = 'roleTable'
    roleId = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(40), unique=True, nullable=False)


class healerTable(db.Model):
    __tablename__ = 'healerTable'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    healerId = db.Column(db.String(15), unique=True, nullable=True)
    emailId = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    mobile = db.Column(db.String(20), nullable=True)
    createdDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    roleId = db.Column(db.Integer, db.ForeignKey(
        'roleTable.roleId', ondelete='CASCADE'))
    # role = relationship('roleTable',foreign_keys="roleTable.roleId")


class patientTable(db.Model):
    __tablename__ = 'patientTable'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    userId = db.Column(db.String(20), unique=True, nullable=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(20), nullable=True)
    mobile = db.Column(db.String(20), nullable=True)
    operationUnderGone = db.Column(db.String(30), nullable=True)
    referredBy = db.Column(db.String(30), nullable=True)
    createdDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    roleId = db.Column(db.Integer, db.ForeignKey(
        'roleTable.roleId', ondelete='CASCADE'))
    # role = relationship('roleTable',foreign_Keys="roleTable.roleId")


class problemTable(db.Model):
    __tablename__ = 'problemTable'
    problemId = db.Column(db.Integer, primary_key=True)
    problem = db.Column(db.String(40), nullable=False)
    howLongSuffered = db.Column(db.String(30), nullable=False)
    medicinesFollowed = db.Column(db.String(40), nullable=False)
    acuPoints = db.Column(db.String(40), nullable=False)
    foodSuggestion = db.Column(db.String(40), nullable=False)
    howLongShouldVisit = db.Column(db.String(40), nullable=False)
    attendedBy = db.Column(db.String(30), nullable=False)
    createdDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # patient = relationship('patientTable')
    patientId = db.Column(db.Integer, db.ForeignKey(
        'patientTable.id', ondelete='CASCADE'))


class feedbackTable(db.Model):
    __tablename__ = 'FeedbackTable'
    feedbackId = db.Column(db.Integer, primary_key=True)
    feedback = db.Column(db.String(40), nullable=False)
    createdDate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # problem = relationship('problemTable')
    problemId = db.Column(db.Integer, db.ForeignKey(
        'problemTable.problemId', ondelete='CASCADE'))


@app.route('/logout')
def logout():
    del session['id']
    return redirect('/')


def currentUser():
    if 'id' in session:
        healerId = session['id']
        return healerTable.query.filter_by(id=healerId).first()
    return None


def currentPatient():
    if 'patientId' in session:
        patientId = session['patientId']
        return patientTable.query.filter_by(id=patientId).first()
    return None


def currentProblem():
    if 'problemId' in session:
        problemId = session['problemId']
        return problemTable.query.filter_by(problemId=problemId).first()
    return None





def convertFeedbacks(lst):
    list = []
    for i in lst:
        date = str(i.createdDate)
        updatedDate = date[:10]
        json = [i.feedbackId, i.feedback, str(updatedDate)]
        list.append(json)
    # print("printing in convert feedbacks method")
    # print(list)
    return list


def convertProblems(lst):
    list = []
    for i in lst:
        date = str(i.createdDate)
        updatedDate = date[:10]
        json = [i.problemId, i.problem, i.howLongSuffered,
                i.acuPoints, i.attendedBy, str(updatedDate)]
        list.append(json)
    return list


def Convert(lst):
    list = []
    for i in lst:
        # json = {'name':i.name,'age':i.age,'city':i.city,'gender':i.gender,'mobile':i.mobile,'operationUnderGone':i.operationUnderGone,'userId':i.userId}
        date = str(i.createdDate)
        updatedDate = date[:10]
        json = [i.name, i.age, i.city, i.gender, i.mobile,
                i.operationUnderGone, i.userId, str(updatedDate)]
        list.append(json)
    returningVal = "data : "+str(list)
    # print(returningVal)
    # print(json.dumps(returningVal))
    return list


class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

@app.route('/success',methods=['GET'])
def successMessage():
    return render_template('uploadSuccess.html')

@app.route('/fail',methods=['GET'])
def failMessage():
    return render_template('uploadFailed.html')

@app.route('/importPatientData',methods=['GET','POST'])
def importHealerData():
    if request.method == 'POST':                
        try:
            f = request.files['file']
            df = pd.read_excel(f) 
            idList = df['Id'].tolist()
            UserIdList = df['UserId'].tolist()
            NameList = df['Name'].tolist()
            AgeList = df['Age'].tolist()
            CityList = df['City'].tolist()
            GenderList = df['Gender'].tolist()
            MobileList = df['Mobile'].tolist()  
            SurgeryList = df['Surgery'].tolist()  
            CreatedAtList = df['Created At'].tolist() 
            referredBy = df['Referred By'].tolist() 
            # print("counting the list")
            # print(len(idList))
            lengthOfTheList = len(idList)
            i=0
            try :
                while(i<lengthOfTheList):
                    # print("The date is")
                    # print(datetime.datetime.strptime(CreatedAtList[i], '%Y-%m-%d %H:%M:%S.%f'))
                    patient = patientTable(id=idList[i],name=NameList[i], age=AgeList[i], city=CityList[i], mobile=MobileList[i], gender=GenderList[i], operationUnderGone=SurgeryList[i], userId=UserIdList[i], roleId=3, referredBy=referredBy[i],createdDate=datetime.datetime.strptime(CreatedAtList[i], '%Y-%m-%d %H:%M:%S.%f'))
                    db.session.add(patient)
                    db.session.commit()
                    i+=1
                return redirect('/success')
            except :
                # print("InValid Data")
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                return redirect('/fail')    
        except:
            # print("second exception block")
            # print(str(sys.exc_info()[0]).split(' ')[1].strip(
            #         '>').strip("'")+"-"+(str(sys.exc_info()[1])))
            return redirect('/fail')
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload</h1>
     <form  method = "POST" 
         enctype = "multipart/form-data">
         <input type = "file" name = "file" />
         <input type = "submit"/>
      </form>
    '''


### importing problem data
@app.route('/importProblemData',methods=['GET','POST'])
def importProblemData():
    if request.method == 'POST':                
        try:
            f = request.files['file']
            df = pd.read_excel(f) 
            ProblemIdList = df['ProblemId'].tolist()
            ProblemList = df['Problem'].tolist()
            howLOngSufferedList = df['How Long Suffered'].tolist()
            MedicinesFollowedList = df['Medicines Followed'].tolist()
            AcuPointsUsedList = df['Acu Points Used'].tolist()
            FoodSuggestionList = df['Food Suggestion'].tolist()
            HowLongShouldVisitList = df['How Long Should Visit'].tolist()  
            AttendedByList = df['Attended By'].tolist()  
            CreatedAtList = df['Created Date'].tolist() 
            PatientIdList = df['PatientId'].tolist() 
            # print("counting the list")
            # print(len(ProblemIdList))
            lengthOfTheList = len(ProblemIdList)
            i=0
            try :
                while(i<lengthOfTheList):
                    # print("The date is")
                    # print(datetime.datetime.strptime(CreatedAtList[i], '%Y-%m-%d %H:%M:%S.%f'))
                    problem = problemTable(problemId=ProblemIdList[i],problem=ProblemList[i], howLongShouldVisit=HowLongShouldVisitList[i], medicinesFollowed=MedicinesFollowedList[i],
                                       acuPoints=AcuPointsUsedList[i], patientId=PatientIdList[i], foodSuggestion=FoodSuggestionList[i], howLongSuffered=howLOngSufferedList[i], attendedBy=AttendedByList[i],createdDate=datetime.datetime.strptime(CreatedAtList[i], '%Y-%m-%d %H:%M:%S.%f'))
                    db.session.add(problem)
                    db.session.commit()
                    i+=1
                return redirect('/success')
            except :
                # print("InValid Data")
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                return redirect('/fail')    
        except:
            # print("second exception block")
            # print(str(sys.exc_info()[0]).split(' ')[1].strip(
            #         '>').strip("'")+"-"+(str(sys.exc_info()[1])))
            return redirect('/fail')
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload</h1>
     <form  method = "POST" 
         enctype = "multipart/form-data">
         <input type = "file" name = "file" />
         <input type = "submit"/>
      </form>
    '''

### importing feedback data
@app.route('/importFeedbackData',methods=['GET','POST'])
def importFeedbackData():
    if request.method == 'POST':                
        try:
            f = request.files['file']
            df = pd.read_excel(f) 
            feedbackIdList = df['feedbackId'].tolist()
            feedbackList = df['feedback'].tolist()
            problemIdList = df['problemId'].tolist()            
            CreatedAtList = df['createdDate'].tolist()             
            # print("counting the list")
            # print(len(feedbackIdList))
            lengthOfTheList = len(feedbackIdList)
            i=0
            try :
                while(i<lengthOfTheList):
                    # print("The date is")
                    # print(datetime.datetime.strptime(CreatedAtList[i], '%Y-%m-%d %H:%M:%S.%f'))
                    createdFeedback = feedbackTable(feedbackId=feedbackIdList[i],feedback=feedbackList[i], problemId=problemIdList[i],createdDate=datetime.datetime.strptime(CreatedAtList[i], '%Y-%m-%d %H:%M:%S.%f'))
                    db.session.add(createdFeedback)
                    db.session.commit()
                    i+=1
                return redirect('/success')
            except :
                # print("InValid Data")
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                return redirect('/fail')    
        except:
            # print("second exception block")
            # print(str(sys.exc_info()[0]).split(' ')[1].strip(
            #         '>').strip("'")+"-"+(str(sys.exc_info()[1])))
            return redirect('/fail')
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload</h1>
     <form  method = "POST" 
         enctype = "multipart/form-data">
         <input type = "file" name = "file" />
         <input type = "submit"/>
      </form>
    '''





def writePatientData():
    totalPatient = db.session.query(patientTable).all()
    patientData = []
    if totalPatient:
        for i in totalPatient:
            val = [i.id,i.userId,i.name, i.age, i.city, i.gender, i.mobile,
                i.operationUnderGone,  str(i.createdDate),i.referredBy]
            patientData.append(val)
    return patientData

@app.route('/PatientsDetails', methods=['GET'])
def exportPatient():
    try:
        # print("In the method")
        workbook = xlsxwriter.Workbook('acu-home_Patient.xlsx')
        worksheet = workbook.add_worksheet('firstsheet')
        patientData = writePatientData()
        if patientData:
            worksheet.write(0,0,"Id")
            worksheet.write(0,1,"UserId")
            worksheet.write(0,2,"Name")
            worksheet.write(0,3,"Age")        
            worksheet.write(0,4,"City")
            worksheet.write(0,5,"Gender")        
            worksheet.write(0,6,"Mobile")
            worksheet.write(0,7,"Surgery")
            worksheet.write(0,8,"Created At")
            worksheet.write(0,8,"Rferred By")
            row = 1
            col = 0
            # print("THis is row value outside for"+str(row))
            # print("THis is col value outside for "+str(col))
            for Id,UserId,Name,Age,City,Gender,Mobile,Surgery,CreatedAt,referredBy in (patientData):
                # print("THis is row value "+str(row))
                # print("THis is col value "+str(col))
                worksheet.write(row,col,Id)
                worksheet.write(row,col + 1,UserId)
                worksheet.write(row,col + 2,Name)
                worksheet.write(row,col + 3,Age)        
                worksheet.write(row,col + 4,City)
                worksheet.write(row,col + 5,Gender)        
                worksheet.write(row,col + 6,Mobile)
                worksheet.write(row,col + 7,Surgery)
                worksheet.write(row,col + 8,CreatedAt)
                worksheet.write(row,col + 9,referredBy)
                row+=1
            workbook.close()
            return send_file('acu-home_Patient.xlsx',cache_timeout=0)
        return "No Patient Found"
    except:
        # print(str(sys.exc_info()[0]).split(' ')[1].strip(
        #             '>').strip("'")+"-"+(str(sys.exc_info()[1])))
        return "Exception"

def writeHealerData():
    totalHealer = db.session.query(healerTable).all()
    healerData = []
    if totalHealer:
        for i in totalHealer:
            val = [i.id,i.healerId,i.name, i.emailId, i.password, i.mobile, str(i.createdDate)]
            healerData.append(val)
    return healerData


@app.route('/exportHealerData',methods=['GET'])
def exportHealer():
    try:
        workbook = xlsxwriter.Workbook('acu-home_Healer.xlsx')
        worksheet = workbook.add_worksheet('firstsheet')
        healerData = writeHealerData()
        if healerData:
            worksheet.write(0,0,"Id")
            worksheet.write(0,1,"healerId")
            worksheet.write(0,2,"Name")
            worksheet.write(0,3,"Email Id")        
            worksheet.write(0,4,"Password")                   
            worksheet.write(0,5,"Mobile")            
            worksheet.write(0,6,"Created At")
            row = 1
            col = 0
            for id,healerId,name,emailId,password,mobile,createdDate in (healerData):
                # print("THis is row value "+str(row))
                # print("THis is col value "+str(col))
                worksheet.write(row,col,id)
                worksheet.write(row,col + 1,healerId)
                worksheet.write(row,col + 2,name)
                worksheet.write(row,col + 3,emailId)
                worksheet.write(row,col + 4,password)        
                worksheet.write(row,col + 5,mobile)
                worksheet.write(row,col + 6,createdDate)
                row+=1
            workbook.close()
            return send_file('acu-home_Healer.xlsx',cache_timeout=0)
        return "No Patient Found"
    except:
        return "Exception"



def writeProblemData():
    totalProblems = db.session.query(problemTable).all()
    problemData = []
    if totalProblems:
        for i in totalProblems:
            val = [i.problemId,i.problem,i.howLongSuffered, i.medicinesFollowed, i.acuPoints, i.foodSuggestion,i.howLongShouldVisit,i.attendedBy,i.patientId,str(i.createdDate)]
            problemData.append(val)
    return problemData


@app.route('/ProblemDetails',methods=['GET'])
def exportProblemDetails():
    try:
        workbook = xlsxwriter.Workbook('acu-Home_problemDetails.xlsx')
        worksheet = workbook.add_worksheet('firstSheet')
        problemData = writeProblemData()
        if problemData:
            worksheet.write(0,0,"ProblemId")
            worksheet.write(0,1,"Problem")
            worksheet.write(0,2,"How Long Suffered")
            worksheet.write(0,3,"Medicines Followed")        
            worksheet.write(0,4,"Acu Points Used")                   
            worksheet.write(0,5,"Food Suggestion")            
            worksheet.write(0,6,"How Long Should Visit")
            worksheet.write(0,7,"Attended By")
            worksheet.write(0,8,"PatientId")
            worksheet.write(0,9,"Created Date")
            row = 1
            Col = 0
            for problemId,problem,howLongSuffered,medicinesFollowed,acuPoints,foodSuggestion,howLongShouldVisit,attendedBy,patientId,createdDate in (problemData):
                worksheet.write(row,Col,problemId)
                worksheet.write(row,Col+1,problem)
                worksheet.write(row,Col+2,howLongSuffered)
                worksheet.write(row,Col+3,medicinesFollowed)        
                worksheet.write(row,Col+4,acuPoints)                   
                worksheet.write(row,Col+5,foodSuggestion)            
                worksheet.write(row,Col+6,howLongShouldVisit)
                worksheet.write(row,Col+7,attendedBy)
                worksheet.write(row,Col+8,patientId)
                worksheet.write(row,Col+9,createdDate)
                row+=1
            workbook.close()
            return send_file('acu-Home_problemDetails.xlsx',cache_timeout=0)
        return "No data found"
    except:
        return "Exception"

def writeFeedbackData():
    totalFeedback = db.session.query(feedbackTable).all()
    feedbackData = []
    if totalFeedback:
        for i in totalFeedback:
            val = [i.feedbackId,i.feedback,i.problemId,str(i.createdDate)]
            feedbackData.append(val)
    return feedbackData
        

@app.route('/FeedbackDetails',methods=['GET'])
def exportFeedback():
    try:
        workbook = xlsxwriter.Workbook('acu-Home_feedbackDetails.xlsx')
        worksheet = workbook.add_worksheet('firstSheet')
        feedbackData = writeFeedbackData()
        if feedbackData:
            worksheet.write(0,0,"feedbackId")
            worksheet.write(0,1,"feedback")
            worksheet.write(0,2,"problemId")
            worksheet.write(0,3,"createdDate")
            row = 1
            Col = 0
            for feedbackId,feedback,problemId,createdDate in (feedbackData):
                worksheet.write(row,Col,feedbackId)
                worksheet.write(row,Col+1,feedback)
                worksheet.write(row,Col+2,problemId)
                worksheet.write(row,Col+3,createdDate)  
                row+=1
            workbook.close()
            return send_file('acu-Home_feedbackDetails.xlsx',cache_timeout=0)
        return "No data Found"
    except:
        return "Exception"    

@app.route('/problemDetails', methods=['GET', 'POST'])
def problemDetails():
    if request.method == 'POST':
        formType = request.form.get('formType')
        # print("in problemDetails recieved form is " + formType)
        if formType == 'editForm':
            problemId = request.form.get('problemId')
            problem = request.form.get('problem')
            howLongSuffered = request.form.get('howLongSuffered')
            medicinesFollowed = request.form.get('medicinesFollowed')
            acuPoints = request.form.get('acuPoints')
            foodSuggestion = request.form.get('foodSuggestion')
            howLongShouldVisit = request.form.get('howLongShouldVisit')
            try:
                retrievedProblem = problemTable.query.filter_by(
                    problemId=problemId).first()
                retrievedProblem.problem = problem
                retrievedProblem.howLongSuffered = howLongSuffered
                retrievedProblem.medicinesFollowed = medicinesFollowed
                retrievedProblem.acuPoints = acuPoints
                retrievedProblem.foodSuggestion = foodSuggestion
                retrievedProblem.howLongShouldVisit = howLongShouldVisit
                db.session.commit()
                updatedProblem = problemTable.query.filter_by(
                    problemId=problemId).first()
                feedbackList = feedbackTable.query.filter_by(
                    problemId=problemId).all()
                feedbackJson = []
                if feedbackList:
                    feedbackJson = convertFeedbacks(feedbackList)
                # print(feedbackJson)
                return redirect('problemDetails')
                # return render_template('/problemDetails.html',feedbacks=json.dumps(feedbackJson),problem=updatedProblem,successMessage="Problem Updated Successfully")
            except:
                nonUpdatedProblem = problemTable.query.filter_by(
                    problemId=problemId).first()
                feedbackList = feedbackTable.query.filter_by(
                    problemId=problemId).all()
                feedbackJson = []
                if feedbackList:
                    feedbackJson = convertFeedbacks(feedbackList)
                # print(feedbackJson)
                return "Error"
                # return render_template('/problemDetails.html',feedbacks=json.dumps(feedbackJson),problem=nonUpdatedProblem,errorMessage="Not Updated")
        if formType == 'deleteForm':
            problemId = request.form.get('problemId')
            try:
                problemToFindPatient = problemTable.query.filter_by(
                    problemId=problemId).first()
                patientId = problemToFindPatient.patientId
                problemToBeDeleted = problemTable.query.filter_by(
                    problemId=problemId).delete()
                db.session.commit()
                deletedFeedbacks = db.session.query(
                    feedbackTable).filter_by(problemId=problemId).delete()
                db.session.commit()
                patientDetails = patientTable.query.filter_by(
                    id=patientId).first()
                # print(patientDetails.userId)
                problemsJson = []
                problemsList = problemTable.query.filter_by(
                    patientId=patientId).all()
                if problemsList:
                    problemsJson = convertProblems(problemsList)
                return redirect('/individualPatient')
                # return render_template('individualPatient.html',patient=patientDetails,problems=json.dumps(problemsJson),successMessage="Deleted Successfully")
            except:
                # print('in the exception method')
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                nonDeletedProblem = problemTable.query.filter_by(
                    problemId=problemId).first()
                feedbackJson = []
                feedbackList = feedbackTable.query.filter_by(
                    problemId=problemId).all()
                if feedbackList:
                    feedbackJson = convertFeedbacks(feedbackList)
                # print(feedbackJson)
                return "Error"                
        if formType == 'addForm':
            problemId = request.form.get('problemId')
            try:
                feedback = request.form.get('feedback')
                createdFeedback = feedbackTable(
                    feedback=feedback, problemId=problemId)
                db.session.add(createdFeedback)
                db.session.commit()
                feedbackJson = []
                feedbackList = feedbackTable.query.filter_by(
                    problemId=problemId).all()
                if feedbackList:
                    feedbackJson = convertFeedbacks(feedbackList)
                detailedProblemInfo = problemTable.query.filter_by(
                    problemId=problemId).first()
                # print(feedbackJson)
                return redirect('/problemDetails')                
            except:
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                feedbackJson = []
                feedbackList = feedbackTable.query.filter_by(
                    problemId=problemId).all()
                feedbackJson = []
                if feedbackList:
                    feedbackJson = convertFeedbacks(feedbackList)
                detailedProblemInfo = problemTable.query.filter_by(
                    problemId=problemId).first()
                # print(feedbackJson)
                return "Error"                
        if formType == 'editFeedbackForm':
            try:
                feedBackId = request.form.get('feedbackId')
                feedback = request.form.get('feedback')
                retrievedFeedback = feedbackTable.query.filter_by(
                    feedbackId=feedBackId).first()
                retrievedFeedback.feedback = feedback
                db.session.commit()
                return redirect('/problemDetails')
            except:
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                return "Exception"
        if formType == 'deleteFeedbackForm':
            try:
                
                feedBackId = request.form.get('feedbackId')
                # print("feedback id received "+feedBackId)
                deletedFeedback = feedbackTable.query.filter_by(
                    feedbackId=feedBackId).delete()
                db.session.commit()
                return redirect('/problemDetails')
            except:
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                return "Exception"
    crntPrblm = currentProblem()
    user = currentUser()
    if user and crntPrblm:
        feedbacksList = feedbackTable.query.filter_by(
            problemId=crntPrblm.problemId).all()
        # print("printing the feedback list")
        # print(feedbacksList)
        feedbackJson = []
        if feedbacksList:
            feedbackJson = convertFeedbacks(feedbacksList)
        # print("printing feedback json")
        # print(feedbackJson)      
        return render_template('/problemDetails.html', healer=user, problem=crntPrblm, feedbacks=json.dumps(feedbackJson))        
    return redirect('/')




@app.route('/individualPatient', methods=['GET', 'POST'])
def indPatient():
    if request.method == 'POST':
        formType = request.form.get('formType')
        # print("form type is " + formType)
        if formType == 'editForm':
            userId = request.form.get('userId')
            name = request.form.get('name')
            age = request.form.get('age')
            city = request.form.get('city')
            gender = request.form.get('gender')
            mobile = request.form.get('mobile')
            operationUnderGone = request.form.get('operationUnderGone')
            try:
                retrievedPatient = patientTable.query.filter_by(
                    userId=userId).first()
                retrievedPatient.name = name
                retrievedPatient.age = age
                retrievedPatient.city = city
                retrievedPatient.gender = gender
                retrievedPatient.mobile = mobile
                retrievedPatient.operationUnderGone = operationUnderGone
                db.session.commit()
                patientDetails = patientTable.query.filter_by(
                    userId=userId).first()
                problemsJson = []
                problemsList = problemTable.query.filter_by(
                    patientId=patientDetails.id).all()
                # print(problemsList)
                if problemsList:
                    problemsJson = convertProblems(problemsList)
                return redirect('/individualPatient')
                # return render_template('/individualPatient.html',problems=json.dumps(problemsJson),patient=patientDetails,successMessage=patientDetails.name + "  updated Successfully")
            except:
                patientDetails = patientTable.query.filter_by(
                    userId=userId).first()
                problemsJson = []
                problemsList = problemTable.query.filter_by(
                    patientId=patientDetails.id).all()
                # print(problemsList)
                if problemsList:
                    problemsJson = convertProblems(problemsList)
                return "Error"
                # return render_template('/individualPatient.html',problems=json.dumps(problemsJson),patient=patientDetails,errorMessage=patientDetails.name + "  Not Updated")
        formType = request.form.get('formType')
        if formType == 'deleteForm':
            userId = request.form.get('userId')
            try:
                # print("in try method with userId " + userId)
                patientToBedeleted = patientTable.query.filter_by(
                    userId=userId).first()
                allProblemsOfAPatient = db.session.query(problemTable).all()
                if allProblemsOfAPatient:
                    for i in allProblemsOfAPatient:
                        db.session.query(feedbackTable).filter(feedbackTable.problemId==i.problemId).delete()
                db.session.query(problemTable).filter(problemTable.patientId==patientToBedeleted.id).delete()
                db.session.commit()
                pt = patientTable.query.filter_by(userId=userId).delete()                
                db.session.commit()                                
                # print('patient is deleted')                
                return redirect('/patientPage')
                # return render_template('/patientPage.html', successMessage=userId + "  deleted Successfully", patients=json.dumps(allPatientsJson))
            except:
                # print('in the exception method')
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                patientDetails = patientTable.query.filter_by(
                    userId=userId).first()
                problemsJson = []
                problemsList = problemTable.query.filter_by(
                    patientId=patientDetails.id).all()
                # print(problemsList)
                if problemsList:
                    problemsJson = convertProblems(problemsList)
                #tempPt = patientTable.query.filter_by(id=patientDetails.id).first()
                return "Error"
                # return render_template('/individualPatient.html',problems=json.dumps(problemsJson),patient=patientDetails,errorMessage= "  Not deleted")
        if formType == 'addForm':
            try:
                userId = request.form.get('userId')
                problem = request.form.get('problem')
                howLongSuffered = request.form.get('howLongSuffered')
                medicinesFollowed = request.form.get('medicinesFollowed')
                acuPoints = request.form.get('acuPoints')
                foodSuggestion = request.form.get('foodSuggestion')
                howLongShouldVisit = request.form.get('howLongShouldVisit')
                attendedBy = request.form.get('attendedBy')
                temp = patientTable.query.filter_by(userId=userId).first()
                problem = problemTable(problem=problem, howLongShouldVisit=howLongShouldVisit, medicinesFollowed=medicinesFollowed,
                                       acuPoints=acuPoints, patientId=temp.id, foodSuggestion=foodSuggestion, howLongSuffered=howLongSuffered, attendedBy=attendedBy)
                db.session.add(problem)
                db.session.commit()
                problemsJson = []
                patientDetails = patientTable.query.filter_by(
                    userId=userId).first()
                problemsList = problemTable.query.filter_by(
                    patientId=patientDetails.id).all()
                # print(problemsList)
                if problemsList:
                    problemsJson = convertProblems(problemsList)
                # print(convertProblems(problemsList))
                return redirect('/individualPatient')
                # return render_template('/individualPatient.html',patient=patientDetails,problems=json.dumps(problemsJson),successMessage="Problem added Successfully")
            except:
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                patientDetails = patientTable.query.filter_by(
                    userId=userId).first()
                problemsList = problemTable.query.filter_by(
                    patientId=patientDetails.id).all()
                problemsJson = []
                if problemsList:
                    problemsJson = convertProblems(problemsList)
                return "Error"
                # return render_template('/individualPatient.html',patient=patientDetails,problems=json.dumps(problemsJson) ,errorMessage= "Problem Not added")
        if formType == 'problemDetailsTable':
            problemId = request.form.get('problemId')
            detailedProblemInfo = problemTable.query.filter_by(
                problemId=problemId).first()
            # print("the problem id received is "+problemId)
            session['problemId'] = problemId
            # feedbacksList = feedbackTable.query.filter_by(problemId=problemId).all()
            # print("printing the feedback list")
            # print(feedbacksList)
            # feedbackJson = []
            # if feedbacksList:
            #     feedbackJson = convertFeedbacks(feedbacksList)
            # print("printing feedback json")
            # print(feedbackJson)
            # allfeedback = db.session.query(feedbackTable).all()
            # print("printing allfeedback ")
            # for i in range(len(allfeedback)):
            #     print(allfeedback[i].problemId)
            return redirect('/problemDetails')
            # return render_template('/problemDetails.html',problem=detailedProblemInfo,feedbacks=json.dumps(feedbackJson))
    crntPatient = currentPatient()
    crntUser = currentUser()
    crntprblm = currentProblem()
    if crntprblm:
        del session['problemId']
    if crntUser and crntPatient:
        #totalPatient = db.session.query(patientTable).all()
        #allPatientsJson = []
        # if totalPatient:
        #    allPatientsJson = Convert(totalPatient)
        problemsList = problemTable.query.filter_by(
            patientId=crntPatient.id).all()
        problemsJson = []
        if problemsList:
            problemsJson = convertProblems(problemsList)
        return render_template('individualPatient.html', healer=crntUser, patient=crntPatient, problems=json.dumps(problemsJson))
    return redirect('/')


@app.route('/Dashboard')
def testDashboard():
    user = currentUser()
    if user:
        roles = roleTable.query.filter_by(roleId=user.roleId).first()
        healersCount = healerTable.query.all()
        totalPatientsCount = db.session.query(patientTable).count()
        totalHealersCount = db.session.query(healerTable).count()
        totalPatient = db.session.query(patientTable).all()
        return render_template('testDashboard2.html', healer=user, role=roles.role, healersCount=totalHealersCount, patientsCount=totalPatientsCount)
    else:
        return redirect('/')


# @app.route('/tesingIndPtnt', methods=['GET', 'POST'])
# def tesingIndPtnt():
#     if request.method == 'GET':
#         # content = request.get_json()
#         # receivedPatientId = content['patientId']
#         receivedPatientId = request.args.get('patientId')
#         print("patient Id from form "+receivedPatientId)
#         patientDetails = patientTable.query.filter_by(
#             userId=receivedPatientId).first()
#         print(patientDetails.userId)
#         totalPatient = db.session.query(patientTable).all()
#         allPatientsJson = []
#         if totalPatient:
#             allPatientsJson = Convert(totalPatient)
#         problemsList = problemTable.query.filter_by(
#             patientId=patientDetails.id).all()
#         problemsJson = []
#         if problemsList:
#             problemsJson = convertProblems(problemsList)
#         return render_template('individualPatient.html', patient=patientDetails, problems=json.dumps(problemsJson), patients=json.dumps(allPatientsJson))


@app.route('/patientPage', methods=['GET', 'POST'])
def patientPage():
    if request.method == 'POST':
        if request.form.get('formType') == 'addPatientForm':
            receivedName = request.form.get('name')
            # print(receivedName)
            age = request.form.get('age')
            # print(age)
            gender = request.form.get('gender')
            # print(gender)
            city = request.form.get('city')
            # print(city)
            operationUnderGone = request.form.get('operationUnderGone')
            # print(operationUnderGone)
            referredBy = request.form.get('referredBy')
            # print(referredBy)
            mobile = request.form.get('mobile')
            # print(mobile)
            patientCount = db.session.query(patientTable).count()
            patientCount = patientCount + 1
            patientId = "ACUPTNT-"+str(patientCount)
            while patientCount > 0:
                patientId = "ACUPTNT-"+str(patientCount)
                patient = patientTable.query.filter_by(
                    userId=patientId).first()
                if patient:
                    patientCount = patientCount + 1
                    continue
                else:
                    break
            try:
                patient = patientTable(name=receivedName.capitalize(), age=age, city=city.capitalize(), mobile=mobile, gender=gender.capitalize(
                ), operationUnderGone=operationUnderGone, userId=patientId, roleId=3, referredBy=referredBy.capitalize())
                db.session.add(patient)
                db.session.commit()
            except:
                # print(str(sys.exc_info()[0]).split(' ')[1].strip(
                #     '>').strip("'")+"-"+(str(sys.exc_info()[1])))
                return "Exception"
            # createdHealer = healerTable.query.filter_by(emailId=emailId).first()
            createdPatient = patientTable.query.filter_by(
                userId=patientId).first()
            if createdPatient:
                session['patientId'] = createdPatient.id
                return redirect('/individualPatient')
            return "Exception"

        receivedPatientId = request.form.get('patientId')
        # print("patient Id from form "+receivedPatientId)
        patientDetails = patientTable.query.filter_by(
            userId=receivedPatientId).first()
        if patientDetails:
            # print(patientDetails.userId)
            session['patientId'] = patientDetails.id
            return redirect('/individualPatient')
        return "Exception"
        # totalPatient = db.session.query(patientTable).all()
        # allPatientsJson = []
        # if totalPatient:
        #     allPatientsJson = Convert(totalPatient)
        # problemsList = problemTable.query.filter_by(patientId=patientDetails.id).all()
        # problemsJson = []
        # if problemsList:
        #     problemsJson = convertProblems(problemsList)
        # return render_template('individualPatient.html',patient=patientDetails,problems=json.dumps(problemsJson),patients=json.dumps(allPatientsJson))
    crnttPatient = currentPatient()
    if crnttPatient:
        del session['patientId']
    user = currentUser()
    allPatientsJson = []
    totalPatient = db.session.query(patientTable).all()
    # if totalPatient and user:
    #         roles = roleTable.query.filter_by(roleId=user.roleId).first()
    #         allPatientsJson = Convert(totalPatient)
    if user:
        if totalPatient:
            roles = roleTable.query.filter_by(roleId=user.roleId).first()
            allPatientsJson = Convert(totalPatient)
            return render_template('patientPage.html', healer=user, patients=json.dumps(allPatientsJson))
        return render_template('patientPage.html', healer=user, patients=json.dumps(allPatientsJson))
    else:
        return redirect('/')


# @app.route('/addPatient', methods=['GET', 'POST'])
# def addPatient():
#     if request.method == 'POST':
#         receivedName = request.form.get('name')
#         print(receivedName)
#         age = request.form.get('age')
#         print(age)
#         gender = request.form.get('gender')
#         print(gender)
#         city = request.form.get('city')
#         print(city)
#         operationUnderGone = request.form.get('operationUnderGone')
#         print(operationUnderGone)
#         referredBy = request.form.get('referredBy')
#         print(referredBy)
#         mobile = request.form.get('mobile')
#         print(mobile)
#         patientCount = db.session.query(patientTable).count()
#         patientCount = patientCount + 1
#         patientId = "ACUPTNT-"+str(patientCount)
#         while patientCount > 0:
#             patientId = "ACUPTNT-"+str(patientCount)
#             patient = patientTable.query.filter_by(userId=patientId).first()
#             if patient:
#                 patientCount = patientCount + 1
#                 continue
#             else:
#                 break
#         try:
#             patient = patientTable(name=receivedName.capitalize(), age=age, city=city.capitalize(), mobile=mobile, gender=gender.capitalize(
#             ), operationUnderGone=operationUnderGone, userId=patientId, roleId=3, referredBy=referredBy.capitalize())
#             db.session.add(patient)
#             db.session.commit()
#         except:
#             print(str(sys.exc_info()[0]).split(' ')[1].strip(
#                 '>').strip("'")+"-"+(str(sys.exc_info()[1])))
#             return "Exception"
#         # createdHealer = healerTable.query.filter_by(emailId=emailId).first()
#         createdPatient = patientTable.query.filter_by(userId=patientId).first()
#         print(createdPatient.name)
#         totalPatient = db.session.query(patientTable).all()
#         allPatientsJson = []
#         if totalPatient:
#             allPatientsJson = Convert(totalPatient)
#         return redirect('/patientPage')
       
#     user = currentUser()
#     roles = roleTable.query.filter_by(roleId=user.roleId).first()
#     allpatients = db.session.query(patientTable).all()
#     print(type(allpatients))
#     for i in allpatients:
#         print(i.name)
#     if user:
#         return render_template('addPatient.html', healer=user)
#     else:
#         return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        emailId = request.form.get('email')
        password = request.form.get('password')
        doesEmailExist = healerTable.query.filter_by(emailId=emailId).first()
        error = None
        if doesEmailExist:
            if doesEmailExist.password != password:
                error = "Invalid Credentials"
                return render_template('login.html', error=error)
            else:
                session['id'] = doesEmailExist.id
                return redirect('/')
        else:
            error = "Invalid Credentials"
            return render_template('login.html', error=error)
    user = currentUser()
    if user:
        return redirect('/Dashboard')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        emailId = request.form.get('email')
        password = request.form.get('password')
        error = None
        checkUserExist = healerTable.query.filter_by(emailId=emailId).first()
        checkMobileNumExist = healerTable.query.filter_by(
            mobile=mobile).first()
        if checkMobileNumExist:
            error = 'Mobile Number already exists'
            return render_template('signup.html', error=error)
        if checkUserExist:
            error = 'Email already exists'
            return render_template('signup.html', error=error)
        healerCount = db.session.query(healerTable).count()
        healerCount = healerCount + 1
        healerId = "ACUHLR-"+str(healerCount)
        while healerCount > 0:
            healerId = "ACUHLR-"+str(healerCount)
            healer = healerTable.query.filter_by(healerId=healerId).first()
            if healer:
                healerId = healerId + 1
                continue
            else:
                break
        # print(healerId)
        healer = healerTable(name=name.capitalize(
        ), mobile=mobile, emailId=emailId, password=password, healerId=healerId, roleId=2)
        db.session.add(healer)
        db.session.commit()
        createdHealer = healerTable.query.filter_by(emailId=emailId).first()
        message = createdHealer.name.capitalize() + ' Login Now'
        return render_template('signup.html', successMessage=message)
        # return render_template('dashboard.html',healer=createdHealer)
    roleTableCount = db.session.query(roleTable).count()
    if roleTableCount == 0:
        roleObject = [roleTable(role="Admin"), roleTable(
            role="Healer"), roleTable(role="Patient")]
        db.session.add_all(roleObject)
        db.session.commit()
    roleTableCount = db.session.query(roleTable).count()

    return render_template('signup.html')

def open_browser():
      webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    CORS(app)
    app.secret_key = 'development'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///acuhome.sqlite3'
    db.create_all()
    app.secret_key = 'development'
    app.run(debug=True)
