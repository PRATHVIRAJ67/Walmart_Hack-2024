from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import pymongo
import traceback

users_bp = Blueprint("users_bp", __name__)

# MongoDB client
myclient = pymongo.MongoClient(
    "mongodb+srv://genaigcp62:Royals@wallmart.zjrlc.mongodb.net/?retryWrites=true&w=majority&appName=wallmart"
)
mydb = myclient["mydatabase"]
collection = mydb["users"]

# Initialize the collection and insert some initial data
def initialize_users_collection():
    try:
        # Drop the collection if it already exists
       
        # Create the collection
        mydb.create_collection("users")

       
    except Exception as e:
        print(f"Error initializing users collection: {e}")
        print(traceback.format_exc())

# Call the function to initialize the users collection and data
initialize_users_collection()

@users_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.json  # Get JSON data from the request

        # Extract fields from the JSON data
        first_name = data.get("firstName")
        last_name = data.get("lastName")
        phone = data.get("phone")
        email = data.get("email")
        password = data.get("password")

        if not all([first_name, last_name, phone, email, password]):
            return jsonify({"error": "Missing required fields"}), 400

        password = password.encode("utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        collection.insert_one(
            {
                "firstName": first_name,
                "lastName": last_name,
                "phone": phone,
                "email": email,
                "password": hashed,
            }
        )
        return jsonify({"success": "Registration successful"}), 200
    except Exception as e:
        print(f"Error during registration: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500
    
@users_bp.route("/login", methods=["POST"])
def login():
    try:
        email = request.form.get("email")
        password = request.form.get("password").encode("utf-8")

        user = collection.find_one({"email": email})
        if not user:
            return jsonify({"error": "Wrong login credentials"}), 400

        hashed = user["password"]
        if bcrypt.checkpw(password, hashed):
            encoded_jwt = jwt.encode(
                {"id": str(user["_id"])}, "SignedByRK", algorithm="HS256"
            )
            return jsonify({"token": encoded_jwt}), 200
        else:
            return jsonify({"error": "Wrong login credentials"}), 400
    except Exception as e:
        print(f"Error during login: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@users_bp.route("/getuser")
def getuser():
    try:
        user = request.environ.get("user")
        if user:
            return jsonify({"username": user["firstName"] + " " + user["lastName"]}), 200
        else:
            return jsonify({"error": "Invalid authorization"}), 400
    except Exception as e:
        print(f"Error getting user: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500
