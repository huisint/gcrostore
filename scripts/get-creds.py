#! /usr/bin/env python

import os

from google_auth_oauthlib import flow

import gcrostore

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ.get("CLIENT_ID", ""),
        "project_id": "crostore-363522",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get("CLIENT_SECRET", ""),
        "redirect_uris": ["http://localhost"],
    }
}


def main() -> None:
    oauth_flow = flow.InstalledAppFlow.from_client_config(
        CLIENT_CONFIG, scopes=gcrostore.config.scopes
    )
    creds = oauth_flow.run_console()
    print(creds.to_json())


if __name__ == "__main__":
    main()
