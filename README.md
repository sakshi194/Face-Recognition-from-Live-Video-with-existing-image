# Face-Recognition-from-Live-Video-with-existing-image

## Project Overview

This project is a web-based application built with Flask, OpenCV, and the `face_recognition` library.  
It provides real-time face recognition using a webcam, along with functionalities to upload, capture, and manage face images.

The application allows users to:

- Recognize known faces in real time  
- Add new faces to the database  
- Delete or manage existing face images  

---

## Features

### ✔ Real-time Face Recognition  
Streams live video from the user's webcam and identifies known faces.

### ✔ Upload Face Images  
Users can upload images of new faces to add them to the recognition database.

### ✔ Capture Face Images  
Capture images directly from the webcam and save them.

### ✔ Manage Face Images  
View all saved face images and delete any unwanted ones.

### ✔ Display Recognized Faces  
Shows the names of detected faces during live video feed.

---

## Technologies Used

- **Flask** – Lightweight Python web framework  
- **OpenCV** – Computer vision and image processing  
- **face_recognition** – Python library for face recognition  
- **HTML / CSS / JavaScript** – Frontend UI  
- **SQLite** – Stores encoded face data persistently  

---

## Usage

### 🔹 Real-time Face Recognition
- Open the home page to view the webcam stream.  
- The system will automatically detect and identify faces.

### 🔹 Upload Face Images
- Navigate to the "Upload Image" page.  
- Enter the person's name and upload their photo.

### 🔹 Capture Face Images
- Go to "Capture Face Image".  
- Take a picture using the webcam and save it with a name.

### 🔹 Manage Face Images
- View all stored images in the gallery.  
- Delete any image as needed.

---

