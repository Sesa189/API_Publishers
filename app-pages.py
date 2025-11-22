import asyncio
import json
from bson import ObjectId

import tornado.web
from pymongo import AsyncMongoClient
from motor.motor_asyncio import AsyncIOMotorClient as AsyncMongoClient

class PublishersHandler(tornado.web.RequestHandler):
    async def get(self, publisher_id=None):
        if not publisher_id:
            name = self.get_query_argument("name", default=None)
            country = self.get_query_argument("country", default=None)
            found = []
            if name or country:
                documents = publishers_collection.find({"$or": [{"name": name}, {"country": country}]})
            else:
                documents = publishers_collection.find()
            async for document in documents:
                document["_id"] = str(document["_id"])
                found.append(document)
            self.write(json.dumps(found))
        else:
            if publisher_id:
                doc = await publishers_collection.find_one({"_id": ObjectId(publisher_id)})
                doc["_id"] = str(doc["_id"])
                self.write(doc)


class BooksHandler(tornado.web.RequestHandler):
    async def get(self):
        pass

def make_app():
    return tornado.web.Application([
        (r"/publishers", PublishersHandler),
        (r"/publishers/([0-9a-fA-F]{24})", PublishersHandler),
        (r"/publishers/([0-9a-fA-F]{24})/books", BooksHandler),
        (r"/publishers/([0-9a-fA-F]{24})/books/([0-9a-f]{24})", BooksHandler)
    ])

async def main(shutdown_event):
    app = make_app()
    app.listen(8888)
    print("Server attivo su http://localhost:8888/publishers")
    await shutdown_event.wait()
    print("Chiusura server...")

if __name__ == "__main__":
    client = AsyncMongoClient("localhost", 27017)
    db = client["publisher_db"]
    publishers_collection = db["publishers"]
    books_collection = db["books"]
    shutdown_event = asyncio.Event()
    try:
        asyncio.run(main(shutdown_event))
    except KeyboardInterrupt:
        shutdown_event.set()
