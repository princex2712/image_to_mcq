import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    config = {
    "apiKey": "AIzaSyAwotS8vgdkKUWasgA2655YVzlC0RcYgOk",
    "authDomain": "imagetotext-e82d4.firebaseapp.com",
    "databaseURL": "https://imagetotext-e82d4-default-rtdb.firebaseio.com",
    "projectId": "imagetotext-e82d4",
    "storageBucket": "imagetotext-e82d4.appspot.com",
    "messagingSenderId": "882423195064",
    "appId": "1:882423195064:web:7f1584d61d52cf00b01b4d",
    "serviceAccount": "serviceAccount.json"
    }
    cred = credentials.Certificate(config["serviceAccount"])
    firebase_admin.initialize_app(cred, {'storageBucket': config['storageBucket']})