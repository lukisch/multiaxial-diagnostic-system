"""Configuration for the Diagnostic Testcenter."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(BASE_DIR, "tests")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
PDFS_DIR = os.path.join(BASE_DIR, "pdfs")
DB_PATH = os.path.join(BASE_DIR, "testcenter.db")

# Flask
SECRET_KEY = os.environ.get("TESTCENTER_SECRET", "dev-key-change-in-production")
HOST = os.environ.get("TESTCENTER_HOST", "0.0.0.0")
PORT = int(os.environ.get("TESTCENTER_PORT", 5050))
DEBUG = os.environ.get("TESTCENTER_DEBUG", "false").lower() == "true"

# Session link expiry in hours (0 = no expiry)
SESSION_EXPIRY_HOURS = int(os.environ.get("TESTCENTER_SESSION_EXPIRY", 72))

# Default language
DEFAULT_LANG = os.environ.get("TESTCENTER_LANG", "de")
