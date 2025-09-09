


# 🔍 Phishing URL Detector

## 🌐 Live Demo

[🔗 View Phishing URL Detector live:](https://phishing-detector-c1t4.onrender.com/)   https://phishing-detector-c1t4.onrender.com/  


A simple **machine learning-based web app** built with **Flask** that detects whether a given URL is **legitimate or phishing**.

## 🚀 Features
- Extracts features from URLs to detect phishing attempts  
- Trained ML pipeline stored in `phishdetector_v1.pkl`  
- Flask web app with responsive HTML + CSS  
- Light/Dark mode toggle 🌙☀️  
- Easy to deploy locally or via tools like **ngrok**

---

## 📂 Project Structure
```markdown

phishing_detector/
│── app_flask.py # Flask application
│── train.py # Training script for the ML model
│── features.py # Feature extraction functions
│── model/ # Saved ML model (.pkl)
│── templates/
│ └── index.html # Frontend HTML
│── static/
│ ├── style.css # Stylesheet (with dark mode)
│ ├── script.js # JavaScript (e.g., dark mode toggle)
│ └── favicon.ico # Website favicon
│── README.md # Documentation

````

---

## 🛠️ Installation & Setup

### 1. Clone the repository
```
git clone git@github.com:your-username/phishing_detector.git
cd phishing_detector
````

### 2. Create and activate a virtual environment

```
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Train the model (optional, if you want to retrain)

```
python train.py
```

This saves the model into `model/phishdetector_v1.pkl`.

### 5. Run the Flask app

```
python app_flask.py
```

Go to: **[http://127.0.0.1:8080/](http://127.0.0.1:8080/)**

---

## 🌐 Remote Access

To share your app over the internet, you can use [ngrok](https://ngrok.com/):

```
ngrok http 8080
```

---

## 📸 Screenshots




<img width="1439" height="777" alt="Screenshot 2025-08-21 at 1 43 59 PM" src="https://github.com/user-attachments/assets/888b03e3-55c7-4bb1-9499-e864157f666d" />

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## 📜 License

This project is licensed under the MIT License.

```

---

👉 Do you want me to also create a **requirements.txt** for your project automatically, so others can install dependencies easily?
```
