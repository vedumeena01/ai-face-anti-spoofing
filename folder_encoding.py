import face_recognition
import pickle
import os
from cryptography.fernet import Fernet

# --- Create or load encryption key ---
if not os.path.exists('secret_folder.key'):
    key = Fernet.generate_key()
    with open('secret_folder.key', 'wb') as key_file:
        key_file.write(key)
else:
    with open('secret_folder.key', 'rb') as key_file:
        key = key_file.read()

fernet = Fernet(key)

# --- Encode faces ---
base_dir = 'known_faces_folder'  # Folder containing subfolders of people
known_encodings = []
known_names = []

print("🔍 Encoding known faces...")

for person_name in os.listdir(base_dir):
    person_path = os.path.join(base_dir, person_name)
    if not os.path.isdir(person_path):
        continue  # skip files, only use folders for people

    print(f"\n👤 Processing {person_name}:")

    for filename in os.listdir(person_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(person_path, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(person_name)
                print(f"   ✅ Encoded {filename}")
            else:
                print(f"   ⚠️ No face detected in {filename}")

# --- Encrypt and save data ---
data = pickle.dumps({'names': known_names, 'encodings': known_encodings})
encrypted_data = fernet.encrypt(data)

with open('encodings_secure_folder.pickle', 'wb') as f:
    f.write(encrypted_data)

print("\n🔐 All encodings saved securely as 'encodings_secure_folder.pickle'")
print(f"📦 Total encoded faces: {len(known_encodings)}")
print(f"👥 Total unique people: {len(set(known_names))}")
