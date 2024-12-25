import urllib
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Any

username = "sandeep"
password = "peedn@sT7"
encoded_username = urllib.parse.quote_plus(username)
encoded_password = urllib.parse.quote_plus(password)
MONGO_STRING = f"mongodb+srv://{encoded_username}:{encoded_password}@owlit-cluster.s4cvt.mongodb.net/?retryWrites=true&w=majority&appName=owlit-cluster"
DATABASE_NAME = "owlit"

'''
Design Pattern Name:
Centralized Repository Manager
Lazy Loading with Predefined Collections
Centralized Management: The RepositoryManager handles repository initialization and ensures single-instance reuse.
No Repetition: Accessing repositories like repo_manager.users eliminates repetitive initialization code.
Scalability: Adding new repositories is as simple as adding a new attribute in the manager.
Lazy Initialization: You can initialize repositories on demand if needed (get_repository approach).
'''


class MongoRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, data: dict) -> Any:
        return await self.collection.insert_one(data)

    async def read(self, query: dict) -> Any:
        return await self.collection.find_one(query)

    async def read_all(self, query: dict = {}) -> list:
        cursor = self.collection.find(query)
        return await cursor.to_list(length=None)

    async def update(self, query: dict, update_data: dict) -> Any:
        return await self.collection.update_one(query, {"$set": update_data})

    async def delete(self, query: dict) -> Any:
        return await self.collection.delete_one(query)

    async def upsert(self, query: dict, update_data: dict) -> Any:
        return await self.collection.update_one(query, {"$set": update_data}, upsert=True)

    async def add_to_array_field(self, query: dict, array_field: str, item_data: dict) -> Any:
        update_data = {
            "$addToSet": {array_field: item_data}  # Push the new item into the array
        }
        return await self.collection.update_one(query, update_data, upsert=True)

    # take cares both partial and complete pull
    async def remove_from_array_field(self, query: dict, array_field: str, item_data: dict) -> Any:
        update_data = {
            "$pull": {array_field: item_data}
        }
        return await self.collection.update_one(query, update_data)


class JobRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def add_job(self, id: str, user_id: str, func_name: str, args: dict, target_time: datetime):
        job_data = {
            "_id": id,
            "user_id": user_id,
            "func_name": func_name,
            "args": args,
            "target_time": target_time,
        }
        return await self.collection.insert_one(job_data)

    async def get_job(self, job_id: str):
        return await self.collection.find_one({"_id": job_id})

    async def update_job(self, job_id: str, updates: dict):
        return await self.collection.update_one({"_id": job_id}, {"$set": updates})

    async def delete_job(self, job_id: str):
        return await self.collection.delete_one({"_id": job_id})

    async def get_all_jobs(self):
        cursor = self.collection.find({})
        return await cursor.to_list(length=None)

    async def upsert_job(self, job_id: str, job_data: dict):
        return await self.collection.update_one(
            {"job_id": job_id}, {"$set": job_data}, upsert=True
        )


class RepositoryManager:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.users = MongoRepository(self.db["users"])
        self.paid_subscribers = MongoRepository(self.db["paid_subscribers"])
        self.token_base = MongoRepository(self.db["token_base"])
        self.posts = MongoRepository(self.db["posts"])
        self.jobs = JobRepository(self.db["jobs"])
        self.webhooks = MongoRepository(self.db["webhooks"])


repo_manager = RepositoryManager(uri=MONGO_STRING, db_name=DATABASE_NAME)
