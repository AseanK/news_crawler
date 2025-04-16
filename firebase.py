import firebase_admin
from firebase_admin import firestore_async
from firebase_admin import credentials

class Firebase:
    def __init__(self):
        # cred = credentials.Certificate(r'/Users/krean/misk/stock-b81fc-firebase-adminsdk-fbsvc-39563d6b26.json') ## MAC
        cred = credentials.Certificate(r'/home/krean/misk/stock-b81fc-firebase-adminsdk-fbsvc-ac0438ae97.json') ## LINUX
        firebase_admin.initialize_app(cred)

        self.db = firestore_async.client()


    async def create_news(self, heading, data, timestamp):
        collection_name = "news"
    
        inp = {
            'heading': heading,
            'summary': data["summary"],
            'impacts': data['impacts'],
            'timestamp': timestamp,
            'views': 0,
        }

        doc_ref = self.db.collection(collection_name).document()
        await doc_ref.set(inp)


    async def create_events(self, date, events):
        collection_name = "events"

        doc_ref = self.db.collection(collection_name).document(date)

        await doc_ref.set(events)
        
