# app/lib/redact.py

"""
Redaction utilities for sensitive data
"""

def redact(text: str, secrets: list[str]) -> str:
    """
    Redact sensitive strings from text
    """
    redacted = text
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "<REDACTED>")
    return redacted