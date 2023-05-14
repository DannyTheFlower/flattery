from keras.applications import ResNet50
from keras.applications.resnet import preprocess_input
from keras.utils.image_utils import img_to_array
from sklearn.neighbors import NearestNeighbors
import io
from PIL import Image
import sqlite3
import numpy as np

model = ResNet50(weights=None, include_top=False, pooling='avg')
model.load_weights('weights.h5')


def extract_features(img_array):
    img = Image.fromarray(img_array.astype(np.uint8))
    img = img.resize((224, 224))
    img_data = img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)
    features = model.predict(img_data)
    return features.flatten()


def add_photo(id, features):
    conn = sqlite3.connect('rentals.db')
    cur = conn.cursor()
    features_string = features.tobytes()
    cur.execute("INSERT INTO photos (id, features) VALUES (?, ?)", (id, features_string))
    conn.commit()
    conn.close()


def get_photos():
    conn = sqlite3.connect('rentals.db')
    cur = conn.cursor()
    cur.execute("SELECT photo FROM rentals")
    photos = []
    for row in cur.fetchall():
        photo = Image.open(io.BytesIO(row[0]))
        photo = img_to_array(photo)
        photos.append(photo)
    conn.close()
    return photos


def create_features_table():
    conn = sqlite3.connect('rentals.db')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE photos (
            id INTEGER PRIMARY KEY,
            features STRING
        )
    """)
    conn.close()


def find_similar_images(input_img):
    conn = sqlite3.connect('rentals.db')
    cur = conn.cursor()
    cur.execute("SELECT id, features FROM photos")
    db_features = []
    ids = []
    for row in cur.fetchall():
        features = np.frombuffer(row[1], dtype=np.float32)
        db_features.append(features)
        ids.append(row[0])
    conn.close()

    input_features = extract_features(input_img)
    nbrs = NearestNeighbors(n_neighbors=3, algorithm='ball_tree').fit(db_features)
    distances, indices = nbrs.kneighbors([input_features])
    similar_image_ids = [ids[i] for i in indices.flatten()]
    return similar_image_ids


"""
create_features_table()
photos = get_photos()
for i, photo in enumerate(photos):
    features = extract_features(photo)
    add_photo(i + 1, features)
"""
