import gridfs
import json
from bson import ObjectId
from flask import Flask, render_template, request, jsonify, Response, url_for, redirect
from flask_cors import CORS, cross_origin
from mongoDBOperations import MongoDBManagement
from logger_class import getLog
import os
from gtts import gTTS
import pymongo
import base64
from werkzeug.utils import secure_filename
from bson import json_util
import json
from flask import Flask, flash, request, redirect, url_for
import datetime
import pyttsx3
import speake3
logger = getLog('log.txt')

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)

dbname = 'Create-Loquis-Form'
dbname1 = 'image_Create-Loquis-Form'
form_collection_name = 'clumpcoder1'
log_signup_collection_name = "log_sign"

user_name = 'guider'
password = 'guider'

url ="mongodb+srv://guider:guider@cluster0.kaevq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

app = Flask(__name__)
app.json_encoder = MyEncoder

app.config['UPLOAD_FOLDER'] = '/home/ubuntu/'
app.config['MAX_CONTENT_PATH'] = 5*1024*1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
lst = {'mp3','wav'}
lst1 = {'txt'}

def allowed_file(filename,allowed_items):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_items



from flask import send_from_directory

app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True)


@app.route('/uploads/<name>',methods=['GET'])
@cross_origin()
def download_file(name):
   return send_from_directory(app.config["UPLOAD_FOLDER"], name)
textToSpeechName=''
@app.route('/uploader', methods = ['GET', 'POST'])
@cross_origin()
def upload_file():
    file_list = []
    if request.method == 'POST':
        i = 1

        while int(i) <= int(len(request.files)):
        # check if the post request has the file part
            if (request.form['text'+str(i)]):
                print(request.form['text'+str(i)])
                textToSpeechName = text_to_speech(request.form['text'+str(i)])
                file_list.append((textToSpeechName))
            if len(request.files) == 0:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file'+str(i)]

            l = [' ', '%', '$', "@", "^", "&", "*", "/", "!"]
            for k in l:
                if k in file.filename:

                    op1 = {"status": "Failed to upload",
                            "message": "Filename should not contain space and special symbols"}
                    return (json.dumps(op1, default=json_util.default))
            date_time = datetime.datetime.now()

            timestamp = date_time.timestamp()
            file.filename = str(timestamp)+file.filename

            file_list.append(file.filename)
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if i > 1:
                if not (allowed_file(file.filename,lst)):
                    op11 = {"status": "Failed to upload",
                       "message": "Please enter mp3 or wav file"}
                    return (json.dumps(op11, default=json_util.default))

            if i == 1:
                if not (file and allowed_file(file.filename,ALLOWED_EXTENSIONS)):
                    op11 = {"status": "Failed to uplaod",
                            "message": "Please enter png,jpg,jpeg"}
                    return (json.dumps(op11, default=json_util.default))

            try:

                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                path = (redirect(url_for('download_file', name=filename)))
            except Exception as e:
                op1 = {"status": "Failed to uplaod",
                                        "message": "Due to error"}
                return (json.dumps(op1, default=json_util.default))
            i+=1
            new_dict = {
            "status": "success",
            "filename": file_list,
                    }

    return (json.dumps(new_dict, default=json_util.default))

"""def upload_file():
    if request.method == 'POST':
        i=1
        while i <= len(request.files):
            temp = request.files['file'+str(i)]
            temp.save('/home/ubuntu/'+ secure_filename(temp.filename))
            i+=1
        return 'file uploaded successfully'

"""

@app.route('/getdetails',methods=['GET'])
@cross_origin()
def send_details():
    if request.method == 'GET':
        mongoclient = MongoDBManagement(username=user_name,password=password)
        op = mongoclient.findAllRecords(db_name=dbname,collection_name=form_collection_name)
        i=0
        while i< len(op):

            op[i]['Image'] = mongoclient.get_image_from_db_by_id(dbname1,'fs.files',op[i]['Image'])
            i+=1
        return (json.dumps(op, default=json_util.default))


@app.route('/getdetailsbyid/<id>',methods=['GET'])
@cross_origin()
def send_detailsbyid(id):
    mongoclient = MongoDBManagement(username=user_name,password=password)
    op = mongoclient.get_by_id(dbname,form_collection_name, id)
    mongoClient = MongoDBManagement(username=user_name,password=password)
    op['Image'] = mongoClient.get_image_from_db_by_id(dbname1,'fs.files',op['Image'])

    return (json.dumps(op, default=json_util.default))


######-----------------------------------------------------------------------------------------------------------######
######-------------------------------------------Form Input API--------------------------------------------------######
######-----------------------------------------------------------------------------------------------------------######



@app.route('/FormInput',methods=['POST'])
@cross_origin()
def loquis():
    """
    :param : address
    :param : Coordinate
    :param : Channel
    :param : Publication_date
    :param : Expiration_date
    :param : Action_range
    :param : Image
    :return: Acknowledgement
    """
    if request.method == 'POST':
        address = request.json['address']
        Coordinate = request.json['Coordinate']

        Channel = request.json['Channel']
        Publication_date= request.json['Publication_date']
        Expiration_date = request.json['Expiration_date']
        Action_range = request.json['Action_range']
        Image = request.json['Image']

        try:
            #-------For Image-------#
            connection = pymongo.MongoClient(url)
            connection = pymongo.MongoClient(url)
            db = connection[dbname1]

            path = '/home/ubuntu/'+Image
            filedata = open(path,"rb")
            data = filedata.read()
            fs = gridfs.GridFS(db)
            obj_id = fs.put(data,filename = Image)
            Image = obj_id
            image_url = (redirect(url_for('download_file', name=Image)))
            Oliver = request.json['Oliver']
            for temp in Oliver:
                select_language= temp['select_language']
                title = temp['title']
                description = temp['description']
                link = temp['link']
                Audio = temp['file']

            # -------For Audio-------#
                connection = pymongo.MongoClient(url)
                db = connection[dbname1]
                path = '/home/ubuntu/'+Audio
                filedata = open(path, "rb")
                data1 = filedata.read()
                fs = gridfs.GridFS(db)
                obj_id1 = fs.put(data1, filename=Image)
                temp['obj_id1']=obj_id1


            mongoclient = MongoDBManagement(username='guider',password="guider")
            logger.info("Client created")
            mongoclient.createDatabase(db_name=dbname)
            mongoclient.createCollection(collection_name=form_collection_name, db_name=dbname)
            record = {'location':{'address':address,'Coordinate':Coordinate},'Channel': Channel,'Image':Image,'Publication_date': Publication_date, 'Expiration_date': Expiration_date ,
                      'Action_range':Action_range,'oliver':Oliver}
            mongoclient.insertRecord(collection_name=form_collection_name, db_name=dbname, record=record)
            op1 = {"status": "200",
                   "message": "uplaoded Successfully"}
        except Exception as e:

            op1 = {"status": "Failed to upload",
                   "message": "Filename should not contain space and special symbols"}
            return (json.dumps(op1, default=json_util.default))

    return (json.dumps(op1, default=json_util.default))

######-----------------------------------------------------------------------------------------------------------######
######-------------------------------------------Sign-up---------------------------------------------------------######
######-----------------------------------------------------------------------------------------------------------######

@app.route('/signup',methods=['POST'])
@cross_origin()
def sign_up():
    """
    :param : name
    :param : email
    :param : password
    :return: Login Successfull
    """

    if request.method == 'POST':
        name = request.json['name']
        email = request.json['email']
        pass_word = request.json['pass_word']

        CONNECTION_URL = "mongodb+srv://guider:guider@cluster0.kaevq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        client = pymongo.MongoClient(CONNECTION_URL)
        db = client[dbname]
        logsin_collection = db[log_signup_collection_name]
        query = {'email': email}

        if logsin_collection.find(query).count()==0:
            record = {"name": name, "email": email, 'pass_word': pass_word}
            logsin_collection.insert(record)
            retJson = {
                "status": 200,
                "msg": "you successfully signed up"
            }
        else:
            retJson = {
                'status': 301,
                'msg': 'user already exists'
            }

    return retJson


######-----------------------------------------------------------------------------------------------------------######
######-------------------------------------------Login api-------------------------------------------------------######
######-----------------------------------------------------------------------------------------------------------######


@app.route('/log_in',methods=['POST'])
@cross_origin()
def log_in():
    """
    :param : email
    :param : password
    :return: Login Successfull
    """

    if request.method == 'POST':

        email = request.json['email']
        pass_word = request.json['pass_word']

        CONNECTION_URL = "mongodb+srv://guider:guider@cluster0.kaevq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        client = pymongo.MongoClient(CONNECTION_URL)
        db = client[dbname]
        logsin_collection = db[log_signup_collection_name]
        query = {'email': email}

        if logsin_collection.find(query).count() == 0:
            op = "Please Register yourself!!"
        else:
            op = "Login Successfull"

    return op


s = 1

def text_to_speech(text):
    print(text)
    global s
    myobj = gTTS(text=text, lang='en', slow=False)
    print(text)
    date_time = datetime.datetime.now()
    timestamp = str(date_time.timestamp())
    name = str(s)+timestamp + 'textToSpeech.mp3'
    myobj.save(os.path.join('/home/ubuntu/', name))
    s +=1
    return name


'''
engine = pyttsx3.init("espeak")  # object creation
        """ RATE"""
        rate = engine.getProperty('rate')  # getting details of current speaking rate
        engine.setProperty('rate', 150)  # setting up new voice rate

        """VOLUME"""
        volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
        engine.setProperty('volume', 0.9)  # setting up volume level  between 0 and 1

        """VOICE"""
         # getting details of current voice
        voices = engine.getProperty('voices')
        engine.setProperty('voice', 'english+f2')

        """Saving Voice to a file"""
'''


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)