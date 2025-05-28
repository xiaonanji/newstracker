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