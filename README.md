<div align="center">

# 🔬 ColonSightAI

### Explainable Clinical Decision Support System for Colon Cancer Detection Using Deep Learning

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-blue?style=for-the-badge)]()

</div>

---

## 📋 Overview

**ColonSightAI** is a production-grade, AI-powered web application that detects colon cancer from histopathology images using deep learning. Built with **Clean Architecture** principles, it provides an explainable, scalable, and modern clinical decision support system.

### Key Features

- 🧠 **EfficientNetB0 Deep Learning** — Transfer learning-based classification
- 🔍 **Grad-CAM Explainability** — Visual explanations of AI decisions
- 📊 **Interactive Dashboard** — Real-time statistics and prediction history
- 📄 **PDF Diagnostic Reports** — Professional reports generated with ReportLab
- 👥 **Patient Management** — Complete CRUD with unique patient identifiers
- 🔐 **Role-Based Authentication** — Admin, Clinician, and Researcher roles
- 📱 **Responsive Design** — Mobile-first with Bootstrap 5
- 🌙 **Dark Mode** — Professional dark/light theme toggle
- 🔌 **REST API** — JSON endpoints for third-party integrations

---

## 🏗️ Architecture

```
ColonSightAI/
├── app/                        ← Flask application package
│   ├── __init__.py             ← Application factory (create_app)
│   ├── config.py               ← Configuration classes (Dev/Test/Prod)
│   ├── extensions.py           ← Flask extension singletons
│   ├── blueprints/             ← 8 modular route blueprints
│   │   ├── main/               ← Landing page, about, technology
│   │   ├── auth/               ← Login, register, forgot password
│   │   ├── dashboard/          ← User dashboard & statistics
│   │   ├── patient/            ← Patient record CRUD
│   │   ├── prediction/         ← Image upload, AI inference, Grad-CAM
│   │   ├── report/             ← PDF report generation
│   │   ├── admin/              ← Admin dashboard & user management
│   │   └── api/                ← REST API v1 endpoints
│   ├── models/                 ← SQLAlchemy ORM models
│   ├── services/               ← Business logic layer
│   ├── ai/                     ← Deep learning pipeline
│   │   ├── model_config.py     ← Hyperparameters & class labels
│   │   ├── model_loader.py     ← Singleton model loader
│   │   ├── preprocessor.py     ← Image preprocessing pipeline
│   │   ├── predictor.py        ← Inference engine
│   │   └── gradcam.py          ← Grad-CAM heatmap generator
│   ├── utils/                  ← Validators, helpers, decorators, logging
│   ├── static/                 ← CSS, JS, images, vendor libs
│   └── templates/              ← Jinja2 HTML templates
├── data/                       ← Runtime data directories
│   ├── uploads/                ← Uploaded histopathology images
│   ├── heatmaps/               ← Generated Grad-CAM overlays
│   ├── reports/                ← Generated PDF reports
│   ├── models/                 ← Trained model weights (.h5)
│   └── database/               ← SQLite database files
├── docs/                       ← Architecture, API, deployment docs
├── tests/                      ← Pytest test suite
├── scripts/                    ← DB seeding & model training scripts
├── logs/                       ← Application log files
├── run.py                      ← Development entry point
├── wsgi.py                     ← Production WSGI entry point
└── requirements.txt            ← Python dependencies
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript, AOS, GSAP, Lottie, Google Fonts, Font Awesome |
| **Backend** | Python 3.11+, Flask 3.x, Blueprint Architecture |
| **Database** | SQLite via Flask-SQLAlchemy |
| **Deep Learning** | TensorFlow, Keras, EfficientNetB0 (Transfer Learning) |
| **Image Processing** | OpenCV, Pillow, NumPy, Pandas, Matplotlib |
| **Explainability** | Grad-CAM (Gradient-weighted Class Activation Mapping) |
| **Reports** | ReportLab (PDF generation) |
| **Authentication** | Flask-Login, bcrypt, Flask-WTF (CSRF) |
| **Testing** | pytest, pytest-cov, pytest-flask |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ColonSightAI.git
cd ColonSightAI

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env         # Windows
# cp .env.example .env         # macOS/Linux

# Run the development server
python run.py
```

Visit **http://127.0.0.1:5000** in your browser.

---

## 📚 Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and data flow |
| [API.md](docs/API.md) | REST API endpoint documentation |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment guide |

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

---

## 📊 AI Pipeline

```
Upload Image → Validate → Preprocess (224×224, normalize)
    → EfficientNetB0 Inference → Prediction (class + confidence)
    → Grad-CAM Heatmap → Database Storage → PDF Report
```

### Dataset
- **LC25000** — Lung and Colon Cancer Histopathological Images
- 10,000 colon tissue images (5,000 adenocarcinoma + 5,000 normal)
- 768×768 pixels, JPEG format

### Classes
| Class | Label | Description |
|---|---|---|
| `colon_aca` | Colon Adenocarcinoma | Cancerous tissue |
| `colon_n` | Colon Normal | Benign/healthy tissue |

---

## 📄 License

This project is developed as a **Final Year BE Major Project** for academic purposes.

---

<div align="center">

**Built with ❤️ for advancing healthcare AI**

</div>
