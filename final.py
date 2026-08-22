# webcam_all_faces.py
import os
import cv2
import time
import pickle
import numpy as np
import face_recognition
from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.fernet import Fernet

# Anti-spoof imports (your repo)
from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name

# --------- CONFIG ----------
MODEL_DIR = "./resources/anti_spoof_models"
DEVICE_ID = 0
TOLERANCE = 0.5
SCALE_FACTOR = 2.0        # small_frame = original / SCALE_FACTOR
MAX_WORKERS = 6           # increase if you have CPU/GPU to spare
USE_CNN = False           # set True for more accurate detection (slower)
# --------------------------

# load known encodings (encrypted)
with open("secret_folder.key", "rb") as kf:
    key = kf.read()
fernet = Fernet(key)
with open("encodings_secure_folder.pickle", "rb") as ef:
    enc_encrypted = ef.read()
data = pickle.loads(fernet.decrypt(enc_encrypted))
known_encodings = data["encodings"]
known_names = data["names"]

# init anti-spoof predictor
model_test = AntiSpoofPredict(DEVICE_ID)
image_cropper = CropImage()

def clamp_bbox(x, y, w, h, img_w, img_h):
    x = max(0, int(round(x))); y = max(0, int(round(y)))
    w = int(round(w)); h = int(round(h))
    if x + w > img_w: w = img_w - x
    if y + h > img_h: h = img_h - y
    w = max(1, w); h = max(1, h)
    return x, y, w, h

def run_antispoof(frame, bbox):
    prediction = np.zeros((1,3))
    model_files = [f for f in os.listdir(MODEL_DIR) if os.path.isfile(os.path.join(MODEL_DIR, f))]
    for model_name in model_files:
        h_in, w_in, model_type, scale_val = parse_model_name(model_name)
        params = {"org_img": frame, "bbox": bbox, "scale": scale_val, "out_w": w_in, "out_h": h_in, "crop": True}
        if scale_val is None: params["crop"] = False
        try:
            patch = image_cropper.crop(**params)
            prediction += model_test.predict(patch, os.path.join(MODEL_DIR, model_name))
        except Exception as e:
            # skip on error
            print("antispoof error:", e)
            continue
    label = int(np.argmax(prediction))
    score = float(prediction[0][label]) / 2.0
    is_real = (label == 1)
    return is_real, score

def process_face(frame, full_bbox, face_encoding):
    x, y, w, h = full_bbox
    img_h, img_w = frame.shape[:2]
    x, y, w, h = clamp_bbox(x, y, w, h, img_w, img_h)
    bbox = (x, y, w, h)
    is_real, score = run_antispoof(frame, bbox)
    name = "Unknown"
    if len(known_encodings) > 0:
        dists = face_recognition.face_distance(known_encodings, face_encoding)
        best = np.argmin(dists)
        if dists[best] <= TOLERANCE:
            name = known_names[best]
    if name != "Unknown" and is_real:
        status = "Authorized"
    elif name != "Unknown" and not is_real:
        status = "Denied (Spoof)"
    elif name == "Unknown" and is_real:
        status = "Denied (Unknown)"
    else:
        status = "Denied (Unknown & Spoof)"
    return {"bbox": bbox, "name": name, "is_real": is_real, "score": score, "status": status}

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam"); return

    print("Press 'q' to quit.")
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05); continue

            frame = cv2.flip(frame, 1)
            # Resize to speed up detection but keep enough resolution to find faces
            small = cv2.resize(frame, (0,0), fx=1.0/SCALE_FACTOR, fy=1.0/SCALE_FACTOR)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            # detect all faces in this frame (every frame)
            detector = "cnn" if USE_CNN else "hog"
            face_locs = face_recognition.face_locations(rgb_small, model=detector)
            face_encs = face_recognition.face_encodings(rgb_small, face_locs)

            futures = []
            for (top, right, bottom, left), enc in zip(face_locs, face_encs):
                # scale back to original frame coordinates
                x = int(left * SCALE_FACTOR)
                y = int(top * SCALE_FACTOR)
                w = int((right - left) * SCALE_FACTOR)
                h = int((bottom - top) * SCALE_FACTOR)
                full_bbox = (x, y, w, h)
                # submit per-face work (recognition + antispoof)
                futures.append(executor.submit(process_face, frame.copy(), full_bbox, enc))

            results = []
            for fut in as_completed(futures):
                try:
                    results.append(fut.result())
                except Exception as e:
                    print("face processing failed:", e)

            # Draw every detected face's result
            for r in results:
                x, y, w, h = r["bbox"]
                name = r["name"]; status = r["status"]; score = r["score"]
                if status == "Authorized": color = (0,255,0)
                elif "Spoof" in status: color = (0,0,255)
                else: color = (0,165,255)
                cv2.rectangle(frame, (x,y), (x+w, y+h), color, 2)
                cv2.putText(frame, f"{name} | {status}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, f"S:{score:.2f}", (x, y+h+18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            cv2.imshow("All-Faces Auth (Webcam)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        executor.shutdown(wait=False)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
