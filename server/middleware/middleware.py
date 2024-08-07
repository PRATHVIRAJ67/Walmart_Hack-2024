from flask import Response
from bson import ObjectId
import jwt
import pymongo

myclient = pymongo.MongoClient(
    "mongodb+srv://genaigcp62:Royals@wallmart.zjrlc.mongodb.net/?retryWrites=true&w=majority&appName=wallmart"
)
mydb = myclient["mydatabase"]
collection = mydb["users"]

class AuthenticationMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Check if the request path is one that requires authentication
        if environ.get("PATH_INFO") in ["/register", "/login"]:
            return self.app(environ, start_response)

        # Extract the authorization token from the 'Authorization' header
        authorization_header = environ.get("HTTP_AUTHORIZATION")

        if authorization_header and authorization_header.startswith("Bearer "):
            token = authorization_header[len("Bearer "):]
            try:
                # Decode the JWT token
                user_data = jwt.decode(token, "SignedByRK", algorithms=["HS256"])
                user_id = ObjectId(user_data["id"])
                
                # Find the user in the database
                user = collection.find_one({"_id": user_id})
                if user:
                    user.pop("password")  # Remove password before sending user details to the endpoint
                    environ["user"] = user
                    return self.app(environ, start_response)
                else:
                    # Handle unauthorized access
                    res = Response("Authorization failed", mimetype="text/plain", status=401)
                    return res(environ, start_response)
            except jwt.ExpiredSignatureError:
                res = Response("Token has expired", mimetype="text/plain", status=401)
                return res(environ, start_response)
            except jwt.InvalidTokenError:
                res = Response("Invalid token", mimetype="text/plain", status=401)
                return res(environ, start_response)

        # If no authorization header is present or invalid
        res = Response("Authorization header missing or invalid", mimetype="text/plain", status=401)
        return res(environ, start_response)
