# ColonSightAI — System Architecture

## Overview

ColonSightAI follows **Clean Architecture** principles to ensure separation of concerns,
testability, and maintainability. The system is divided into distinct layers:

```
┌─────────────────────────────────────────────────────┐
│                    Presentation                      │
│         (Blueprints / Routes / Templates)            │
├─────────────────────────────────────────────────────┤
│                   Business Logic                     │
│              (Services / Decorators)                 │
├─────────────────────────────────────────────────────┤
│                    Data Access                       │
│            (Models / SQLAlchemy ORM)                 │
├─────────────────────────────────────────────────────┤
│                   AI Pipeline                        │
│    (Preprocessor → Model → Predictor → Grad-CAM)    │
├─────────────────────────────────────────────────────┤
│                  Infrastructure                      │
│     (Config / Extensions / Logging / Utilities)      │
└─────────────────────────────────────────────────────┘
```

## Data Flow — Prediction Pipeline

```
User Upload
    │
    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Image       │────▶│ Preprocessor │────▶│  EfficientNetB0  │
│  Validation  │     │ (224×224,    │     │  (TensorFlow /   │
│  (type/size) │     │  normalize)  │     │   Keras)         │
└──────────────┘     └──────────────┘     └────────┬─────────┘
                                                    │
                                          ┌─────────▼─────────┐
                                          │   Prediction       │
                                          │   (class +         │
                                          │    confidence)     │
                                          └─────────┬─────────┘
                                                    │
                          ┌─────────────────────────┼────────────────────┐
                          │                         │                    │
                 ┌────────▼────────┐     ┌──────────▼─────┐   ┌────────▼────────┐
                 │   Grad-CAM      │     │   Database     │   │   PDF Report    │
                 │   Heatmap       │     │   (SQLite)     │   │   (ReportLab)   │
                 └─────────────────┘     └────────────────┘   └─────────────────┘
```

## Blueprint Architecture

| Blueprint     | URL Prefix    | Responsibility                          |
|---------------|---------------|-----------------------------------------|
| `main`        | `/`           | Landing page, about, technology, 404    |
| `auth`        | `/auth`       | Login, register, logout, forgot pw      |
| `dashboard`   | `/dashboard`  | User dashboard & statistics             |
| `patient`     | `/patient`    | Patient record CRUD                     |
| `prediction`  | `/prediction` | Image upload, inference, Grad-CAM       |
| `report`      | `/report`     | PDF report generation & download        |
| `admin`       | `/admin`      | Admin dashboard & user management       |
| `api`         | `/api/v1`     | RESTful API endpoints                   |

## Technology Stack

| Layer          | Technology                                    |
|----------------|-----------------------------------------------|
| Frontend       | HTML5, CSS3, Bootstrap 5, JS, AOS, GSAP, Lottie |
| Backend        | Python 3.11+, Flask 3.x, Blueprint Architecture |
| Database       | SQLite via Flask-SQLAlchemy                   |
| Deep Learning  | TensorFlow, Keras, EfficientNetB0             |
| Image Proc.    | OpenCV, Pillow, NumPy                         |
| Explainability | Grad-CAM                                      |
| Reports        | ReportLab (PDF generation)                    |
| Auth           | Flask-Login, bcrypt, Flask-WTF (CSRF)         |
| Deployment     | Gunicorn / uWSGI, Docker (planned)            |

## Database Schema (ERD)

```
┌────────────────┐         ┌────────────────┐         ┌────────────────┐
│     users      │         │   patients     │         │  predictions   │
├────────────────┤         ├────────────────┤         ├────────────────┤
│ id (PK)        │    ┌───▶│ id (PK)        │◀───┐    │ id (PK)        │
│ username       │    │    │ patient_uid    │    │    │ prediction_uid │
│ email          │    │    │ first_name     │    │    │ patient_id(FK) │──┘
│ password_hash  │    │    │ last_name      │    │    │ user_id (FK)   │──┐
│ role           │    │    │ date_of_birth  │    └────│ original_image │  │
│ is_active      │    │    │ gender         │         │ heatmap_image  │  │
│ created_at     │──┐ │    │ created_by(FK) │─────────│ predicted_class│  │
│ last_login     │  │ │    │ created_at     │         │ confidence     │  │
└────────────────┘  │ │    └────────────────┘         │ report_path    │  │
                    │ │                                │ status         │  │
                    │ └────────────────────────────────│ created_at     │  │
                    └──────────────────────────────────┘────────────────┘──┘
```
