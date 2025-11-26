import asyncio
import json
from bson import ObjectId

import tornado.web
from pymongo import AsyncMongoClient
from motor.motor_asyncio import AsyncIOMotorClient as AsyncMongoClient, AsyncIOMotorClient


def filtra_books(found, title=None ,author=None, genre=None ):
    if title:
        for doc in found:
            if title not in doc["name"]:
                found.remove(doc)
    if author:
        for doc in found:
            if author not in doc["name"]:
                found.remove(doc)
    if genre:
        for doc in found:
            if genre != doc["name"]:
                found.remove(doc)
    return found

class PublishersHandler(tornado.web.RequestHandler):
    async def get(self, publisher_id=None):
        if not publisher_id:
            name = self.get_query_argument("name", default=None)
            country = self.get_query_argument("country", default=None)
            found = []
            search = []
            if name or country:
                if name:
                    search.apped({"name": name})
                if country:
                    search.apped({"country": country})
                documents = publishers_collection.find({"$and": search})
            else:
                documents = publishers_collection.find()
            async for document in documents:
                document["_id"] = str(document["_id"])
                found.append(document)
            self.write(json.dumps(found))
        else:
            if publisher_id:
                doc = await publishers_collection.find_one({"_id": ObjectId(publisher_id)})
                if doc:
                    doc["_id"] = str(doc["_id"])
                    self.set_status(200)
                    self.write(json.dumps(doc))
                else:
                    self.set_status(404)
                    self.write("Publisher inesistente.")

    async def post(self):
        self.set_header("Content-Type", "application/json")
        data = tornado.escape.json_decode(self.request.body)

        if data["name"] and data["founded_year"] and data["country"]:
            doc = {
                "name": data["name"],
                "founded_year": data["founded_year"],
                "country": data["country"]
            }
            result = await publishers_collection.insert_one(doc)
            doc["_id"] = str(result.inserted_id)
            self.set_status(201)
            self.write(doc)

        else:
            self.set_status(400)
            self.write("JSON fornito non valido.")

    async def put(self, publisher_id):
        self.set_header("Content-Type", "application/json")
        data = tornado.escape.json_decode(self.request.body)

        if data["name"] and data["founded_year"] and data["country"]:
            doc = {
                "name": data["name"],
                "founded_year": data["founded_year"],
                "country": data["country"]
            }
            await publishers_collection.replace_one(
                {"_id": ObjectId(publisher_id)},
                doc
            )
            doc["_id"] = publisher_id
            self.set_status(201)
            self.write(doc)
        else:
            self.set_status(500)
            self.write("JSON fornito non valido.")

    async def delete(self, publisher_id):
        result = await publishers_collection.delete_one({"_id": ObjectId(publisher_id)})
        if result.deleted_count == 1:
            self.set_status(201)
            self.write("Publisher eliminato correttamente.")


class BooksHandler(tornado.web.RequestHandler):
    async def get(self, publisher_id, book_id=None):
        if not book_id:
            title = self.get_query_argument("title", default=None)
            author = self.get_query_argument("author", default=None)
            genre = self.get_query_argument("genre", default=None)
            found = []
            search = []
            if title or author or genre:
                if title:
                    search.apped({"title": title})
                if author:
                    search.apped({"author": author})
                if genre:
                    search.apped({"genre": genre})
                documents = books_collection.find({"_id": ObjectId(book_id), "$and": search})
            else:
                documents = books_collection.find()
            async for document in documents:
                document["_id"] = str(document["_id"])
                found.append(document)
            self.write(json.dumps(found))
        else:
            doc = await books_collection.find_one({"_id": ObjectId(book_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                self.set_status(200)
                self.write(json.dumps(doc))
            else:
                self.set_status(404)
                self.write("Libro inesistente.")

    async def post(self, publisher_id):
        self.set_header("Content-Type", "application/json")
        data = tornado.escape.json_decode(self.request.body)

        if data["title"] and data["author"] and data["genre"]:
            doc = {
                "publisher_id": publisher_id,
                "title": data["title"],
                "author": data["author"],
                "genre": data["genre"]
            }
            result = await books_collection.insert_one(doc)
            doc["_id"] = str(result.inserted_id)
            self.set_status(201)
            self.write(doc)

        else:
            self.set_status(400)
            self.write("JSON fornito non valido.")

    async def put(self, publisher_id, book_id):
        self.set_header("Content-Type", "application/json")
        data = tornado.escape.json_decode(self.request.body)

        if data["title"] and data["author"] and data["genre"]:
            doc = {
                "publisher_id": publisher_id,
                "title": data["title"],
                "author": data["author"],
                "genre": data["genre"]
            }
            result = await publishers_collection.insert_one(doc)
            doc["_id"] = str(result.inserted_id)
            await publishers_collection.replace_one(
                {"_id": book_id},
                doc
            )
            self.set_status(201)
            self.write(doc)
        else:
            self.set_status(400)
            self.write("JSON fornito non valido.")

    async def delete(self, publisher_id, book_id):
        await books_collection.delete_one({"publisher_id": publisher_id, "_id": book_id})

def make_app(publishers_collection, books_collection):
    return tornado.web.Application([
        (r"/publishers", PublishersHandler),
        (r"/publishers/([0-9a-fA-F]{24})", PublishersHandler),
        (r"/publishers/([0-9a-fA-F]{24})/books", BooksHandler),
        (r"/publishers/([0-9a-fA-F]{24})/books/([0-9a-fA-F]{24})", BooksHandler)
    ], publishers=publishers_collection, books=books_collection)

async def main():
    app = make_app(publishers_collection, books_collection)
    app.listen(8888)
    print("Server attivo su http://localhost:8888/publishers")

    # Mantieni il server attivo finché non viene interrotto
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Chiusura server...")

if __name__ == "__main__":
    client = AsyncIOMotorClient(
        "mongodb+srv://cesarenappa_db_user:ogGknHucqHIWqAhi@apipublishers.qzfrfsp.mongodb.net/?appName=APIpublishers"
    )
    db = client["publisher_db"]
    publishers_collection = db["publishers"]
    books_collection = db["books"]

    # Avvio del loop compatibile con Windows
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

'''
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
    client = AsyncMongoClient("mongodb+srv://cesarenappa_db_user:ogGknHucqHIWqAhi@apipublishers.qzfrfsp.mongodb.net/?appName=APIpublishers")
    #client = AsyncMongoClient("localhost", 27017)
    db = client["publisher_db"]
    publishers_collection = db["publishers"]
    books_collection = db["books"]
    shutdown_event = asyncio.Event()
    try:
        asyncio.run(main(shutdown_event))
    except KeyboardInterrupt:
        shutdown_event.set()
'''
