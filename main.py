from fastapi import FastAPI, Request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = FastAPI()

@app.post("/")
async def root(request : Request):
    req_info = await request.json()
    print(req_info)
    try:
        cluster = MongoClient("mongodb://localhost:27017/")
        db = cluster["test"]
        collection=db["feature"]
        collection.insert_one(req_info)
        
        str = ''
        # Access the "__id" field
        str+="Feature: "+req_info["_id"]+"\n\n"
        # Access the "elements" list
        elements = req_info["elements"]
        # Traverse the "elements" list
        for element in elements:
            str+=element["tag"]+"\n"
            # Access the "type" field and "name" field
            str+=element["type"]+":"+element["name"]+"\n"
            # Access the "steps" list
            steps = element["steps"]
            # Traverse the "steps" list
            for step in steps:
                # Access the "keyword" and "text" fields
                str+=step["keyword"]+" "+step["text"]+"\n"
        return {"message":"File Generated Successfully",
                "string":str}
        
    except PyMongoError as e:
        print("Error inserting data:", e)
        return {"message":"Duplicate KEY",
                "string":''}