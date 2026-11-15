"""CastGuard client and helper functions for filename sanitization."""
import os
import re

def safe_filename(name):
    """Strip any path and unsafe characters from an uploaded filename."""
    name = os.path.basename(name.replace("\\", "/"))
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name.lstrip(".") or "upload.pdf"