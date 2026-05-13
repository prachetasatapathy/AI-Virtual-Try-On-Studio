# AI Virtual Try-On Studio

## Overview
AI Virtual Try-On Studio is a web-based application that allows users to virtually try on clothes using AI-powered pose estimation and image processing. The project consists of a backend (Python), a frontend (HTML/JS/CSS), and an ML model integration for pose detection and image synthesis.

---

## Project Structure

```
virtual_tryon/
├── backend/
│   ├── firebase_config.py
│   ├── main.py
│   ├── requirements.txt
│   └── virtual_tryon_schema.sql
├── frontend/
│   ├── firebase_config.js
│   ├── index.html
│   ├── script.js
│   └── style.css
├── ml_model/
│   ├── model.py
│   ├── pose_landmarker_lite.task
│   ├── test_mp.py
│   ├── utils.py
│   └── verify_mediapipe.py
├── static/
│   └── uploads/
│       └── ... (images)
├── venv311/ (local virtual environment)
├── firebase_admin_key.json (service account key)
└── ...
```

---

## Features
- User authentication and image upload (Firebase)
- AI-based pose estimation and virtual try-on
- Frontend for user interaction
- Backend API for processing and database
- Organized static file storage

---

## Setup Instructions

### 1. Clone the Repository
```
git clone https://github.com/prachetasatapathy/AI-Virtual-Try-On-Studio.git
cd AI-Virtual-Try-On-Studio
```

### 2. Backend Setup
- Create a Python virtual environment (recommended):
  ```
  python -m venv venv311
  venv311\Scripts\activate  # On Windows
  source venv311/bin/activate  # On Linux/Mac
  ```
- Install dependencies:
  ```
  pip install -r virtual_tryon/backend/requirements.txt
  ```
- Add your Firebase Admin SDK key as `firebase_admin_key.json` in the root directory.
- Run the backend server (example):
  ```
  python virtual_tryon/backend/main.py
  ```

### 3. Frontend Setup
- Open `virtual_tryon/frontend/index.html` in your browser.
- Configure `firebase_config.js` with your Firebase project credentials.

### 4. ML Model
- The ML model and pose estimation scripts are in `virtual_tryon/ml_model/`.
- Ensure all required model files are present.

---

## Notes
- Do **not** commit sensitive files (e.g., `firebase_admin_key.json`).
- The `venv311/` folder should not be pushed to GitHub (see `.gitignore`).
- Static images are stored in `virtual_tryon/static/uploads/`.

---

## License
This project is for educational and research purposes.

---

## Contributors
- [prachetasatapathy](https://github.com/prachetasatapathy)
- [abhiramdighe](https://github.com/abhiramdighe)

---

## Acknowledgements
- [Firebase](https://firebase.google.com/)
- [MediaPipe](https://mediapipe.dev/)
- [OpenCV](https://opencv.org/)
