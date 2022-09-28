import os

import crostore

SELENIUM_IMPLICITLY_WAIT = int(os.environ.get("SELENIUM_IMPLICITLY_WAIT", "10"))
"""Time in second to wait for Selenium."""
SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
"""The hostname for SMTP."""
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))
"""The port number for SMTP."""
SMTP_FROM = os.environ.get("SMTP_FROM", "")
"""FROM of messages that the app sends."""
BUGSNAG_API_KEY = os.environ.get("BUGSNAG_API_KEY", "")
"""The API key for Bugsnag."""


# Crostore supported platforms
platforms: list[crostore.AbstractPlatform] = [
    crostore.platforms.mercari.Platform(),
    crostore.platforms.yahoo_auction.Platform(),
]

# Google credentials scopes
scopes = [
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive.file",
]
