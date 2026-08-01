# ColonSightAI — API Documentation (v1)

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

> **TODO**: Implement token-based authentication (JWT or session-based).

All API endpoints (except `/health`) will require authentication via
a Bearer token in the `Authorization` header:

```
Authorization: Bearer <token>
```

---

## Endpoints

### Health Check

```
GET /api/v1/health
```

**Description**: Check API availability and model status.

**Response** `200 OK`:
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "model_loaded": true
}
```

---

### Submit Prediction

```
POST /api/v1/predict
```

**Description**: Upload a histopathology image for AI classification.

**Request**: `multipart/form-data`

| Field      | Type   | Required | Description                    |
|------------|--------|----------|--------------------------------|
| image      | file   | Yes      | Histopathology image (PNG/JPG) |
| patient_id | int    | No       | Associated patient record ID   |

**Response** `200 OK`:
```json
{
    "status": "ok",
    "data": {
        "prediction_id": 42,
        "predicted_class": "colon_aca",
        "display_name": "Colon Adenocarcinoma",
        "confidence": 0.9423,
        "confidence_level": "high",
        "heatmap_url": "/static/heatmaps/gradcam_abc123.png",
        "inference_time_ms": 245.3,
        "model_version": "1.0.0"
    }
}
```

---

### List Predictions

```
GET /api/v1/predictions?page=1&per_page=20
```

**Description**: List all predictions for the authenticated user.

**Query Parameters**:

| Param    | Type | Default | Description          |
|----------|------|---------|----------------------|
| page     | int  | 1       | Page number          |
| per_page | int  | 20      | Results per page     |

---

### Get Prediction Detail

```
GET /api/v1/predictions/{id}
```

**Description**: Get detailed results for a specific prediction.

---

### List Patients

```
GET /api/v1/patients?page=1&per_page=20
```

**Description**: List all patient records.

---

### Get Patient Detail

```
GET /api/v1/patients/{id}
```

**Description**: Get detailed information for a specific patient.

---

### System Statistics

```
GET /api/v1/stats
```

**Description**: Get system-wide statistics.

**Response** `200 OK`:
```json
{
    "status": "ok",
    "total_predictions": 1250,
    "total_patients": 340,
    "total_reports": 890,
    "model_accuracy": 0.9856
}
```

---

## Error Responses

All errors follow this format:

```json
{
    "error": "Human-readable error message"
}
```

| Status Code | Meaning                   |
|-------------|---------------------------|
| 400         | Bad Request               |
| 401         | Unauthorized              |
| 403         | Forbidden                 |
| 404         | Not Found                 |
| 413         | File Too Large            |
| 422         | Unprocessable Entity      |
| 500         | Internal Server Error     |
| 501         | Not Implemented           |
