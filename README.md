# AI Virtual Try-On Studio

## Overview

AI Virtual Try-On Studio is a web-based application developed to provide users with an interactive virtual garment visualization experience through the integration of computer vision, pose estimation, and image processing technologies. The system enables users to upload personal images and virtually visualize garments positioned and aligned according to body posture and proportions.

The project combines a responsive frontend interface with a Python-based backend architecture and machine learning modules for image synthesis and pose analysis. MediaPipe is utilized for human pose estimation, OpenCV for image manipulation and processing, Firebase for authentication services, and FastAPI for backend API management.

---

## Features

* AI-based human pose estimation and body landmark detection
* Virtual garment overlay and proportional alignment
* User authentication using Firebase
* Image upload and processing functionality
* FastAPI-powered backend architecture
* Organized static asset and image management
* Responsive and interactive frontend interface
* Computer vision-driven image synthesis pipeline
* Modular and scalable project structure

---

## Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Firebase SDK

### Backend

* Python 3.11
* FastAPI
* Uvicorn
* Firebase Admin SDK
* MySQL

### Machine Learning and Computer Vision

* MediaPipe
* OpenCV
* NumPy
* Pillow
* rembg

---

## Project Structure

```bash
AI-Virtual-Try-On-Studio/
│
├── backend/
│   ├── firebase_config.py
│   ├── main.py
│   ├── requirements.txt
│   └── virtual_tryon_schema.sql
│
├── frontend/
│   ├── firebase_config.js
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── ml_model/
│   ├── model.py
│   ├── utils.py
│   ├── pose_landmarker_lite.task
│   ├── test_mp.py
│   └── verify_mediapipe.py
│
├── static/
│   └── uploads/
│
├── .gitignore
├── firebase_admin_key.json
└── README.md
```

---

## Installation and Setup

### Clone the Repository

```bash
git clone https://github.com/prachetasatapathy/AI-Virtual-Try-On-Studio.git
cd AI-Virtual-Try-On-Studio
```

---

## Backend Configuration

### Create a Virtual Environment

#### Windows

```bash
python -m venv venv311
venv311\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv311
source venv311/bin/activate
```

---

### Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

### Firebase Configuration

1. Create a Firebase project through the Firebase Console.
2. Download the Firebase Admin SDK credentials file.
3. Rename the downloaded file as:

```bash
firebase_admin_key.json
```

4. Place the file in the root directory of the project.

---

### Frontend Firebase Credentials

Update the Firebase configuration values inside:

```bash
frontend/firebase_config.js
```

---

### Database Setup

Import the SQL schema file:

```bash
backend/virtual_tryon_schema.sql
```

into the MySQL database server.

After importing the schema, update the database credentials inside:

```bash
backend/main.py
```

---

## Running the Backend Server

```bash
cd backend
uvicorn main:app --reload
```

The backend server will run at:

```bash
http://127.0.0.1:8000
```

---

## Running the Frontend

Open a new terminal window and execute:

```bash
cd frontend
python -m http.server 5500
```

Access the application through:

```bash
http://localhost:5500
```

---

## Machine Learning Pipeline

The machine learning module is responsible for:

* detecting body landmarks,
* estimating garment placement,
* resizing clothing assets proportionally,
* and compositing garments onto user images using alpha blending techniques.

The primary image processing logic is implemented within:

```bash
ml_model/model.py
```

---

## Security Considerations

Sensitive files and generated assets are excluded from version control through `.gitignore`.

The following files and directories should never be committed:

* `firebase_admin_key.json`
* `.env`
* virtual environment directories
* generated uploads and result images

---

## Future Enhancements

Potential future improvements include:

* real-time webcam-based virtual try-on,
* advanced garment segmentation,
* multi-garment support,
* AI-based size recommendations,
* improved mobile responsiveness,
* and 3D garment simulation.

---

## Contributors

* Pracheta Satapathy
  [https://github.com/prachetasatapathy](https://github.com/prachetasatapathy)

* Abhiram Dighe
  [https://github.com/abhiramdighe](https://github.com/abhiramdighe)

---

## Acknowledgements

* Firebase
* MediaPipe
* OpenCV
* FastAPI
* Python Software Foundation

---

## License

This project is intended solely for educational and research purposes.
