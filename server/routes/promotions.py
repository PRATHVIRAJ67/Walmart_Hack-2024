from flask import Blueprint, request, jsonify
import pymongo
import base64

promotions_bp = Blueprint("promotions_bp", __name__)

# MongoDB connection
myclient = pymongo.MongoClient(
    "mongodb+srv://genaigcp62:Royals@wallmart.zjrlc.mongodb.net/?retryWrites=true&w=majority&appName=wallmart"
)
mydb = myclient["mydatabase"]
collection = mydb["mycollection"]
search_collection = mydb["searchHistory"]

# Initialize the collections and insert some initial data
def initialize_promotions_collections():
    # Drop the collections if they already exist
    collection.drop()
    search_collection.drop()

    # Create the collections
    mydb.create_collection("mycollection")
    mydb.create_collection("searchHistory")

    # Insert some initial data into the collections
    sample_products = [
        {"article_id": 1, "name": "Product 1", "price": 100, "image": base64.b64encode(b"image1").decode('utf-8')},
        {"article_id": 2, "name": "Product 2", "price": 200, "image": base64.b64encode(b"image2").decode('utf-8')},
        {"article_id": 3, "name": "Product 3", "price": 300, "image": base64.b64encode(b"image3").decode('utf-8')},
        # Add more sample products as needed
    ]

    collection.insert_many(sample_products)

# Call the function to initialize the collections and data
initialize_promotions_collections()

# Endpoint to give 50 products randomly
@promotions_bp.route("/general")
def general():
    try:
        items = collection.aggregate([{"$sample": {"size": 50}}])
        products = []
        for item in list(items):
            item["image"] = base64.b64encode(base64.b64decode(item["image"])).decode("utf-8")
            products.append(item)
        return {"result": products}, 200
    except Exception as e:
        return {"error": str(e)}, 500

# Endpoint to insert the search string of a user in the database
@promotions_bp.route("/setstring", methods=["POST"])
def setstring():
    try:
        user = request.environ["user"]
        if not user:
            return {"error": "User not found"}, 400
        curr_str = request.form["str"]
        try:
            original_str = search_collection.find_one({"user_id": user["_id"]})
            if original_str:
                original_str = original_str["search_string"]
                search_collection.update_one(
                    {"user_id": user["_id"]},
                    {"$set": {"search_string": curr_str + " " + original_str}},
                )
            else:
                search_collection.insert_one(
                    {"user_id": user["_id"], "search_string": curr_str}
                )
        except Exception as e:
            return {"error": str(e)}, 500
        return {"success": "Search string updated"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
