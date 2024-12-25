from pymongo import MongoClient

# MongoDB connection details (adjust this according to your setup)
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "myDatabase"

# Establish MongoDB client connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Create a collection for each file (based on file name)
def create_collection(filename):
    collection_name = filename.split('.')[0]  # Name collection based on file name
    collection = db[collection_name]  # Access collection
    return collection

def get_db():
    """Connect to MongoDB and return the database."""
    client = MongoClient("mongodb://localhost:27017/")  # Change this if you're using a different URI
    return client["your_database_name"]  # Replace 'your_database_name' with your desired database name

def insert_data(collection_name, data):
    collection = db[collection_name]
    formatted_data = [{"name": key, "value": value} for key, value in data]
    collection.insert_many(formatted_data)


