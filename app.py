import os
from flask import Flask, request, render_template
from form_parser import extract_data  # Your logic to extract data
import re
from flask import Flask, request, render_template
from form_parser import extract_data  # Your logic to extract data
from db_utils import create_collection, insert_data, get_db
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection details (adjust this according to your setup)
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "myDatabase"

# Establish MongoDB client connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]  # Use the database specified

# Directory to save uploaded files (if required for any purpose)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('upload.html')  # File upload form

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return "No file part", 400

    files = request.files.getlist('files')
    if not files:
        return "No selected files", 400

    results = []  # Store extracted results for display
    for file in files:
        if file.filename == '':
            continue

        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Extract data logic (your existing function for text extraction)
        extracted_text = extract_data(filepath)
        parsed_data = parse_extracted_text(extracted_text)

        # Insert parsed data into a collection named after the file
        collection_name = file.filename.replace('.', '_')  # Use a sanitized collection name
        insert_data(collection_name, parsed_data)

        results.append({'file': file.filename, 'data': parsed_data})

    return render_template('results.html', results=results)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_name = request.form.get('name', '').strip()
        if not search_name:
            return "Search query cannot be empty.", 400

        matching_collections = []  # Store results for all matching collections
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            # Find documents where the "value" field matches the search
            matches = list(collection.find(
                {"value": {"$regex": search_name, "$options": "i"}},
                {"_id": 0}  # Exclude the `_id` field
            ))
            if matches:
                # Retrieve all documents from the matching collection excluding `_id`
                all_documents = list(collection.find({}, {"_id": 0}))
                matching_collections.append({
                    "collection_name": collection_name,
                    "documents": all_documents
                })

        # If no collections match, return an empty result
        if not matching_collections:
            return render_template('search_results.html', results=[], search_name=search_name)

        # Pass all matching collections and their data to the template
        return render_template('search_results.html', results=matching_collections, search_name=search_name)

    return render_template('search.html')



def parse_extracted_text(text):
    """
    Parse the extracted text into key-value pairs.

    Args:
        text (str): The extracted text.

    Returns:
        list: A list of (key, value) tuples.
    """
    lines = text.split('\n')
    data = []

    for line in lines:
        if ':' in line:  # Assuming key-value pairs are separated by ':'
            key, value = line.split(':', 1)
            data.append((key.strip(), value.strip()))
        else:
            data.append(('Unknown', line.strip()))

    return data

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Create the upload folder if it doesn't exist
    app.run(port=5001, debug=True)
