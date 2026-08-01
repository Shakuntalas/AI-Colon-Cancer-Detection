# 📤 Uploads

## Purpose

This directory stores **uploaded histopathology images** submitted by clinicians for AI analysis. Images are saved here after validation and before preprocessing.

## Accepted Formats

| Format | Extensions | Notes |
|---|---|---|
| JPEG | `.jpg`, `.jpeg` | Most common for histopathology |
| PNG | `.png` | Lossless compression |
| TIFF | `.tif`, `.tiff` | High-resolution microscopy |
| BMP | `.bmp` | Uncompressed bitmap |

## File Size Limits

- **Maximum**: 16 MB per image
- **Typical**: 500 KB – 5 MB for histopathology slides

## File Naming Convention

Uploaded files are renamed using a UUID-based scheme to prevent collisions:

```
{uuid4}_{original_filename}.{ext}
```

Example: `a3f8b2c1-4d5e-6f7a-8b9c-0d1e2f3a4b5c_slide_001.jpg`

## Storage Policy

- Original uploads are preserved for audit trail purposes.
- This directory is excluded from Git tracking (see `.gitignore`).
- Implement periodic cleanup for orphaned uploads.
