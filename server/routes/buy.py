from flask import Blueprint, request, jsonify
import pymongo
import base64

buy_bp = Blueprint("buy_bp", __name__)

# MongoDB connection
myclient = pymongo.MongoClient("mongodb+srv://genaigcp62:Royals@wallmart.zjrlc.mongodb.net/?retryWrites=true&w=majority&appName=wallmart")
mydb = myclient['mydatabase']
dataCollection = mydb['mycollection']
collection = mydb['cart']
storeCollection = mydb['store']

# Initialize the collections and insert some initial data
def initialize_buy_collections():
    # Drop the collections if they already exist
    dataCollection.drop()
    collection.drop()
    storeCollection.drop()

    # Create the collections
    mydb.create_collection("mycollection")
    mydb.create_collection("cart")
    mydb.create_collection("store")

    # Insert some initial data into the collections
    sample_products = [
        {"article_id": 1, "name": "Product 1", "price": 100, "image": base64.b64encode(b"image1").decode('utf-8')},
        {"article_id": 2, "name": "Product 2", "price": 200, "image": base64.b64encode(b"image2").decode('utf-8')},
        {"article_id": 3, "name": "Product 3", "price": 300, "image": base64.b64encode(b"image3").decode('utf-8')},
        # Add more sample products as needed
    ]

    dataCollection.insert_many(sample_products)

# Call the function to initialize the collections and data
initialize_buy_collections()

# Endpoint to add an item to cart
@buy_bp.route("/addtocart", methods=['POST'])
def addtocart():
    try:
        user = request.environ['user']
        article_id = request.form['article_id']
        item = collection.find_one({'user_id': user['_id'], 'article_id': int(article_id)})
        if item:
            return jsonify({"error": "Item already present in cart"}), 400
        else:
            collection.insert_one({'user_id': user['_id'], 'article_id': int(article_id)})
            return jsonify({"success": "Item added to cart"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to get the number of items in cart
@buy_bp.route("/numcart")
def numcart():
    try:
        user = request.environ['user']
        items = collection.find({'user_id': user['_id']})
        return jsonify({"numItems": items.count()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to check whether a given item is present in the cart or not
@buy_bp.route("/checkcart", methods=['POST'])
def checkcart():
    try:
        user = request.environ['user']
        article_id = request.form['article_id']
        item = collection.find_one({'user_id': user['_id'], 'article_id': int(article_id)})
        if not item:
            return jsonify({"result": "Item is not present in cart"}), 400
        else:
            return jsonify({"result": "Item is present in cart"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to return the products present in the cart of a user
@buy_bp.route('/cartitems')
def cartitems():
    try:
        user = request.environ['user']
        items = collection.find({'user_id': user['_id']})
        products = []
        for item in items:
            product = dataCollection.find_one({'article_id': int(item['article_id'])}, {'_id': 0})
            if product:
                product["image"] = base64.b64encode(base64.b64decode(product["image"])).decode('utf-8')
                products.append(product)
            else:
                print(item['article_id'], "not found")
        return jsonify({"result": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to store the products for in-store buying
@buy_bp.route('/store', methods=['POST'])
def store():
    try:
        user = request.environ['user']
        if not user:
            return jsonify({"error": "User not found"}), 400
        items = request.form['items']
        for item in items.split(','):
            storeCollection.insert_one({'user_id': user['_id'], 'article_id': int(item)})
        return jsonify({"success": "Items stored successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to retrieve the products for in-store buying
@buy_bp.route('/getstore')
def getstore():
    try:
        user = request.environ['user']
        if not user:
            return jsonify({"error": "User not found"}), 400
        items = storeCollection.find({'user_id': user['_id']})
        products = []
        for item in items:
            product = dataCollection.find_one({'article_id': item['article_id']}, {'_id': 0})
            product["image"] = base64.b64encode(base64.b64decode(product["image"])).decode('utf-8')
            products.append(product)
        return jsonify({"result": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to empty the user's cart
@buy_bp.route('/emptycart')
def emptycart():
    try:
        user = request.environ['user']
        if not user:
            return jsonify({"error": "User not found"}), 400
        collection.delete_many({'user_id': user['_id']})
        return jsonify({"success": "Cart emptied successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
