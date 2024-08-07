from flask import Flask, request
import pymongo
import base64
from flask_cors import CORS
import middleware.middleware as middleware

app = Flask(__name__)
CORS(app)
app.wsgi_app = middleware.AuthenticationMiddleware(app.wsgi_app)

# MongoDB client
myclient = pymongo.MongoClient(
    "mongodb+srv://genaigcp62:Royals@wallmart.zjrlc.mongodb.net/?retryWrites=true&w=majority&appName=wallmart"
)
mydb = myclient["mydatabase"]
collection = mydb["mycollection"]
search_collection = mydb["searchHistory"]


# Initialize the collections and insert some initial data
def initialize_collections():
    # Drop the collections if they already exist
    collection.drop()
    search_collection.drop()

    # Create the collections
    mydb.create_collection("mycollection")
    mydb.create_collection("searchHistory")

    # Insert some initial data into the collections
    sample_products = [
        {
            "article_id": 1,
            "name": "Product 1",
            "price": 100,
            "image": base64.b64encode(b"sample_image_1").decode("utf-8"),
        },
        {
            "article_id": 2,
            "name": "Product 2",
            "price": 200,
            "image": base64.b64encode(b"sample_image_2").decode("utf-8"),
        },
        {
            "article_id": 3,
            "name": "Product 3",
            "price": 150,
            "image": base64.b64encode(b"sample_image_3").decode("utf-8"),
        },
        # Add more sample products as needed
    ]

    sample_search_history = [
        {"user_id": "user1", "search_string": "Product 1"},
        {"user_id": "user2", "search_string": "Product 2"},
        # Add more sample search history as needed
    ]

    collection.insert_many(sample_products)
    search_collection.insert_many(sample_search_history)


# Call the function to initialize collections and data
initialize_collections()

# Register the blueprints
import routes.users as users

app.register_blueprint(users.users_bp)

import routes.promotions as promotions

app.register_blueprint(promotions.promotions_bp)

import routes.buy as buy

app.register_blueprint(buy.buy_bp)

import search_result

# import recommender


@app.route("/search", methods=["POST"])
def search():
    try:
        searchStr = request.form["searchStr"]
        results = search_result.search_result(searchStr, 50)
        if not len(results):
            return {"error": "No products found"}, 400
        results = results.tolist()
        products = []
        for article_id in results:
            product = collection.find_one({"article_id": article_id}, {"_id": 0})
            if product:
                product["image"] = base64.b64encode(product["image"]).decode("utf-8")
                products.append(product)
            else:
                print(article_id, " not found")
        if not len(products):
            return {"error": "No products found"}, 400
        return {"result": products}, 200
    except:
        return {"error": "Server error"}, 500


@app.route("/getitemdetails", methods=["POST"])
def getItemDetails():
    try:
        article_id = request.form["article_id"]
        if not article_id:
            return {"error": "No product found"}, 400
        article_id = int(article_id)
        item = collection.find_one({"article_id": article_id}, {"_id": 0})
        if not item:
            return {"error": "No product found"}, 400
        item["image"] = base64.b64encode(item["image"]).decode("utf-8")
        return {"result": item}, 200
    except:
        return {"error": "Server error"}, 500


@app.route("/cheaper", methods=["POST"])
def cheaper():
    try:
        article_id = request.form["article_id"]
        if not article_id:
            return {"error": "No product found"}, 400
        article_id = int(article_id)
        givenProduct = collection.find_one({"article_id": article_id}, {"_id": 0})
        items = recommender.recommendations(article_id, 50)
        items = list(items)
        if not len(items):
            return {"error": "No product found"}, 400
        cheaperItems = []
        for item in items:
            item = int(item)
            similar_item = collection.find_one({"article_id": item}, {"_id": 0})
            if similar_item and similar_item["price"] < givenProduct["price"]:
                similar_item["image"] = base64.b64encode(similar_item["image"]).decode(
                    "utf-8"
                )
                cheaperItems.append(similar_item)
            if len(cheaperItems) >= 8:
                break
        return {"result": cheaperItems}, 200
    except:
        return {"error": "Server error"}, 500


@app.route("/toppromotion")
def toppromotion():
    try:
        user = request.environ["user"]
        if not user:
            return {"error": "User not found"}, 400
        search_string = search_collection.find_one({"user_id": user["_id"]})
        search_string = search_string["search_string"]
        results = search_result.search_result(search_string, 3)
        if not len(results):
            return {"error": "No products found"}, 400
        results = results.tolist()
        products = []
        for article_id in results:
            product = collection.find_one({"article_id": article_id}, {"_id": 0})
            if product:
                product["image"] = base64.b64encode(product["image"]).decode("utf-8")
                products.append(product)
            else:
                print(article_id, " not found")
        if not len(products):
            return {"error": "No products found"}, 400
        return {"result": products}, 200
    except:
        return {"error": "Server error"}, 500


@app.route("/promotion")
def promotion():
    try:
        user = request.environ["user"]
        if not user:
            return {"error": "User not found"}, 400
        try:
            search_string = search_collection.find_one({"user_id": user["_id"]})
            search_string = search_string["search_string"]
            results = search_result.search_result(search_string, 200)
            if not len(results):
                return {"error": "No products found"}, 400
            results = results.tolist()
            products = []
            for article_id in results:
                product = collection.find_one({"article_id": article_id}, {"_id": 0})
                if product:
                    product["image"] = base64.b64encode(product["image"]).decode(
                        "utf-8"
                    )
                    products.append(product)
                else:
                    print(article_id, " not found")
            if not len(products):
                return {"error": "No products found"}, 400
            return {"result": products}, 200
        except:  # If a new user makes the request then return 50 random products
            try:
                items = collection.find({}, {"_id": 0}).limit(50)
                products = []
                for item in list(items):
                    item["image"] = base64.b64encode(item["image"]).decode("utf-8")
                    products.append(item)
                return {"result": products}, 200
            except:
                return {"error": "Server error"}, 500
    except:
        return {"error": "Server error"}, 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)  # Start the server at port 8000
