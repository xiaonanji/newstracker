import firebase_admin
from firebase_admin import credentials, db

# Load your service account key JSON file
cred = credentials.Certificate(".\\newstracker-84c7d-firebase-adminsdk-fbsvc-c8b0e70438.json")

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