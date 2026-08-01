"""
ColonSightAI — Logging Configuration
=======================================

Configures structured logging with rotating file handlers and
console output. Called during application factory initialization.

Log Levels:
    - DEBUG      : Detailed diagnostic output (dev only)
    - INFO       : General operational messages
    - WARNING    : Non-critical issues
    - ERROR      : Error events that still allow the app to run
    - CRITICAL   : Severe errors that may prevent the app from running

Log Format:
    ``[2024-08-15 14:30:00] [INFO] [module_name] Message text``
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask


def setup_logging(app: Flask) -> None:
    """
    Configure application-wide logging.

    Sets up:
        1. Console handler (StreamHandler) — always active
        2. File handler (RotatingFileHandler) — rotates at 10 MB, keeps 10 backups

    Parameters
    ----------
    app : Flask
        The Flask application instance.
    """
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    log_file = app.config.get('LOG_FILE', 'logs/colonsightai.log')

    # ── Log format ────────────────────────────────────────────────────
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # ── Console handler ───────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # ── File handler (with rotation) ──────────────────────────────────
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
        encoding='utf-8',
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # ── Attach handlers to Flask's logger ─────────────────────────────
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)

    # ── Also configure the root logger for library output ─────────────
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    app.logger.info(
        'Logging configured — level=%s, file=%s',
        logging.getLevelName(log_level),
        log_file,
    )
