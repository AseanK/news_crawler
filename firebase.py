from datetime import datetime
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

class Firebase:
    def __init__(self):
        cred = credentials.Certificate(r'~/misk/stock-b81fc-firebase-adminsdk-fbsvc-39563d6b26.json')
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()


    def create_data(self, heading, summary):
        collection_name = "news"
    
        inp = {
            'heading': heading,
            'summary': summary,
            'timestamp': datetime.now(),
        }

        doc_ref = self.db.collection(collection_name).document()
        doc_ref.set(inp)

    def read_data(self):
        pass


    def remove_data(self):
        pass
