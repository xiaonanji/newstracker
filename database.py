import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, db

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CREDENTIALS_FILE = "newstracker-84c7d-firebase-adminsdk-fbsvc-c8b0e70438.json"

def _resolve_credentials_file():
    """
    Resolve the Firebase credentials file path, allowing overrides via env var.
    """
    custom_path = os.getenv("FIREBASE_CREDENTIALS_FILE", DEFAULT_CREDENTIALS_FILE)
    cred_path = Path(custom_path)
    if not cred_path.is_absolute():
        cred_path = BASE_DIR / cred_path
    if not cred_path.exists():
        raise FileNotFoundError(f"Firebase credentials file not found: {cred_path}")
    return cred_path

# Load your service account key JSON file
cred = credentials.Certificate(str(_resolve_credentials_file()))

# Initialize the app with the service account and database URL
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://newstracker-84c7d-default-rtdb.firebaseio.com/'
})

def write_to_database(person, record):
    """
    Writes data to the Firebase Realtime Database.
    
    Args:
        data (dict): The data to write to the database.
    """
    ref = db.reference(person)
    for url_id, data in record.items():
        ref.child(url_id).set(data)  # Pushes a new child with a unique key
        
    print("Data written to database successfully.")

def add_person(person_name):
    """
    Adds a person to the /persons node in the Firebase Realtime Database.
    The person's key is a sanitized ID (spaces replaced with underscores),
    and the value is a dict with the original name.
    """
    person_id = person_name.replace(' ', '_')
    persons_ref = db.reference("persons")
    persons_ref.update({person_id: {"name": person_name}})
    print(f"Added '{person_name}' (ID: {person_id}) to the persons list in the database.")
