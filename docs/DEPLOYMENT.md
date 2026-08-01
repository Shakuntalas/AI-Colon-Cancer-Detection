# ColonSightAI — Deployment Guide

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- 4 GB RAM minimum (for TensorFlow model inference)
- 2 GB disk space

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ColonSightAI.git
cd ColonSightAI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (especially SECRET_KEY)
```

### 5. Run Development Server

```bash
python run.py
```

The application will be available at `http://127.0.0.1:5000`.

---

## Production Deployment

### Option 1: Gunicorn (Linux/macOS)

```bash
gunicorn wsgi:app \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

### Option 2: Waitress (Windows)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 wsgi:app
```

### Environment Variables for Production

```bash
FLASK_CONFIG=production
SECRET_KEY=<your-random-64-char-secret>
DATABASE_URL=sqlite:///data/database/colonsightai.db
SESSION_COOKIE_SECURE=True
```

---

## Docker Deployment (Planned)

> **TODO**: Create `Dockerfile` and `docker-compose.yml`.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

---

## Database Migrations

```bash
# Initialise migrations (first time only)
flask db init

# Generate migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade
```

---

## Model Setup

1. Train the model using `scripts/train_model.py` (or obtain pre-trained weights).
2. Place the `.h5` file at `data/models/efficientnetb0_colon.h5`.
3. Verify with the health check endpoint: `GET /api/v1/health`.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Ensure venv is activated and `pip install -r requirements.txt` completed |
| Model not loading | Check `MODEL_PATH` in `.env` and ensure `.h5` file exists |
| Port already in use | Change `FLASK_PORT` in `.env` or kill the process on that port |
| CSRF token missing | Ensure `Flask-WTF` is installed and forms include `{{ csrf_token() }}` |
