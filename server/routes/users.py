from flask import Blueprint, request
import bcrypt
import jwt
import pymongo

users_bp = Blueprint("users_bp", __name__)

# MongoDB client
myclient = pymongo.MongoClient(
    "mongodb+srv://genaigcp62:Royals@wallmart.zjrlc.mongodb.net/?retryWrites=true&w=majority&appName=wallmart"
)
mydb = myclient["mydatabase"]
collection = mydb["users"]


# Initialize the collection and insert some initial data
def initialize_users_collection():
    # Drop the collection if it already exists

    collection.drop()
    # Create the collection
    mydb.create_collection("users")

    # Insert some initial data into the collection
    sample_users = [
        {
            "firstName": "John",
            "lastName": "Doe",
            "phone": "1234567890",
            "email": "john.doe@example.com",
            "password": bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()),
        },
        {
            "firstName": "Jane",
            "lastName": "Smith",
            "phone": "0987654321",
            "email": "jane.smith@example.com",
            "password": bcrypt.hashpw("securepass".encode("utf-8"), bcrypt.gensalt()),
        },
        # Add more sample users as needed
    ]

    collection.insert_many(sample_users)


# Call the function to initialize the users collection and data
initialize_users_collection()


@users_bp.route("/register", methods=["POST"])
def register():
    try:
        print(f"Request data: {request.form}")

        first_name = request.form["firstName"]
        last_name = request.form["lastName"]
        phone = request.form["phone"]
        email = request.form["email"]
        password = request.form["password"]

        print(
            f"First Name: {first_name}, Last Name: {last_name}, Phone: {phone}, Email: {email}, Password: {password}"
        )

        if not all([first_name, last_name, phone, email, password]):
            return {"error": "Missing required fields"}, 400

        password = password.encode("utf-8")
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        collection.insert_one(
            {
                "firstName": request.form["firstName"],
                "lastName": request.form["lastName"],
                "phone": request.form["phone"],
                "email": request.form["email"],
                "password": hashed,
            }
        )
        return {"success": "Registration successful"}, 200
    except:
        return {"error": "Internal server error"}, 400


@users_bp.route("/login", methods=["POST"])
def login():
    try:

        email = request.form["email"]
        password = request.form["password"].encode("utf-8")
        user = collection.find_one({"email": email})
        if not user:
            return {"error": "Wrong login credentials"}, 400
        hashed = user["password"]
        if bcrypt.checkpw(password, hashed):
            encoded_jwt = jwt.encode(
                {"id": str(user["_id"])}, "SignedByRK", algorithm="HS256"
            )
            return {"token": encoded_jwt}, 200
        else:
            return {"error": "Wrong login credentials"}, 400
    except:
        return {"error": "Internal server error"}, 500


@users_bp.route("/getuser")
def getuser():
    try:
        user = request.environ["user"]
        if user:
            return {"username": user["firstName"] + " " + user["lastName"]}, 200
        else:
            return {"error": "Invalid authorization"}, 400
    except:
        return {"error": "Internal server error"}, 500
