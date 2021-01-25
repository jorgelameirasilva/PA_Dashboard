
import pymongo
from bson.objectid import ObjectId 
from pymongo import MongoClient
import json
import pandas as pd
import datetime
import dns
import os

if os.environ["USERNAME"] == "jorgelameira":
    from config import get_credential
    user = get_credential("USERNAME")
    pss = get_credential("PASSWORD")
    CLUSTER = get_credential("CLUSTER")
else:
    user = os.environ["USERNAME"]
    pss = os.environ["PASSWORD"]
    CLUSTER = os.environ["CLUSTER"]

db = "etf"

cnn_str = f"mongodb+srv://{user}:{pss}@{CLUSTER}/{db}?retryWrites=true&w=majority"

cluster = MongoClient(cnn_str, retryWrites=False)

db = cluster["etf"]

def clean_db(collection_name="etf"):
    collection = db[collection_name]
    results = collection.delete_many({})
    return results.acknowledged

def save_in_db(df, etf_name, collection_name="etf"):
    df["etf_name"] = etf_name
    collection = db[collection_name]
    for col in df.columns:
        if df[col].dtype == "timedelta64[ns]":
            df[col]=df[col].astype(str)
    res = collection.insert_many(df.to_dict("records"))


def find_in_db(etf_name, collection_name="etf"):
        collection = db[collection_name]

        res = pd.DataFrame(list(collection.find({"etf_name":etf_name})))
        if etf_name != "etf_description" and collection_name== "etf" and "ctm" in res.columns:
            res = res.sort_values(by=["ctm"])
        elif collection_name =="daily_trends":
            res["date"] = pd.to_datetime(res["date"])
            res = res.sort_values(by=["date"])
        res.reset_index(drop=True, inplace=True)
        return res
