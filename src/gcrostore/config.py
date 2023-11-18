import os

import crostore

SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
"""The hostname for SMTP."""
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))
"""The port number for SMTP."""
SMTP_FROM = os.environ.get("SMTP_FROM", "")
"""FROM of messages that the app sends."""

# Crostore supported platforms
platforms: dict[crostore.AbstractPlatform, str] = {
    crostore.platforms.mercari.Platform(): "D",
    crostore.platforms.yahoo_auction.Platform(): "E",
}

# Google credentials scopes
scopes = [
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets",
]
