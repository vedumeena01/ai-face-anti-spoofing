# Real-Time AI Biometric Anti-Spoofing Security System 🔐👁️

An intelligent, real-time computer vision security pipeline integrating multi-face recognition with a deep learning anti-spoofing ensemble and AES-256 encrypted biometric database.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)](https://opencv.org/)
[![Security](https://img.shields.io/badge/Encryption-AES--256%20Fernet-red.svg)](https://cryptography.io/)

---

## 🌟 Core Capabilities

- **Real-Time Multi-Face Recognition:** Detects, tracks, and identifies multiple individuals concurrently via webcam streams.
- **Deep Anti-Spoofing Defense:** Leverages a Silent-Face Anti-Spoofing deep neural network ensemble to reject physical photo prints, digital screen replays, 3D masks, and silicone cutouts.
- **Encrypted Biometric Store:** All facial encodings and identities are cryptographically stored using AES-256 Fernet symmetric encryption (`secret_folder.key`).
- **High-Throughput Threading:** Multi-threaded frame ingestion and GPU-accelerated inference maintaining 30+ FPS and <50ms decision latency.
- **Dynamic Security Decision Matrix:**

| Status             | Visual Indicator | Classification Description               |
|:-------------------|:-----------------|:-----------------------------------------|
| **Authorized**     | 🟢 Green Box     | Verified known identity + Live human     |
| **Denied (Spoof)** | 🔴 Red Box       | Known identity match but Spoof/Fake face |
| **Denied (Unknown)**| 🟠 Orange Box   | Real live person, but unregistered       |
| **Denied (Both)**  | 🔴/🟠 Warning    | Unregistered identity + Fake presentation|

---

## 🚀 Quick Setup & Usage

### 1. Requirements & Dependencies
```bash
git clone https://github.com/vedumeena01/ai-face-anti-spoofing.git
cd ai-face-anti-spoofing
pip install opencv-python dlib face_recognition cryptography numpy
```

### 2. Generate Encrypted Embeddings
```bash
python folder_encoding.py
```

### 3. Launch Live Security System
```bash
python final.py
```

---

## 👤 Author
- **Vedprakash Meena** ([@vedumeena01](https://github.com/vedumeena01))
