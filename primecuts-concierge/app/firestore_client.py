"""Firestore client for PrimeCuts backend.

Explicitly configured with hardcoded GCP Project ID as a string to prevent
project number resolution errors on Agent Platform.
"""

from google.cloud import firestore

FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-698d519bd637"

_db = None

def get_db() -> firestore.Client:
    """Returns a singleton Firestore client instance with hardcoded project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    return _db
