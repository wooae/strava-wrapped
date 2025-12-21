import json
import os
import requests
import time
from datetime import datetime, timezone
from typing import Any, Dict


STRAVA_TOKEN_FILE = "strava_tokens.json"
STRAVA_BASE_URL = "https://www.strava.com/api/v3"


StravaAthlete = Dict[str, Any]


class StravaClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tokens = self._load_tokens()

    # ---------------------------
    # Token handling
    # ---------------------------

    def _load_tokens(self):
        if os.path.exists(STRAVA_TOKEN_FILE):
            with open(STRAVA_TOKEN_FILE, "r") as f:
                return json.load(f)
        return None

    def _save_tokens(self, tokens):
        with open(STRAVA_TOKEN_FILE, "w") as f:
            json.dump(tokens, f, indent=2)
        self.tokens = tokens

    def _is_token_expired(self):
        return not self.tokens or time.time() >= self.tokens["expires_at"]

    def authenticate(self):
        """Run once to get initial tokens."""
        auth_url = (
            "https://www.strava.com/oauth/authorize"
            f"?client_id={self.client_id}"
            "&response_type=code"
            "&redirect_uri=http://localhost/exchange_token"
            "&approval_prompt=force"
            "&scope=read,activity:read_all"
        )

        print("\nOpen this URL in your browser and authorize the app:\n")
        print(auth_url)
        print("\nPaste the `code` parameter from the redirect URL below:\n")

        code = input("Authorization code: ").strip()
        self._exchange_code_for_token(code)

    def _exchange_code_for_token(self, code):
        response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        self._save_tokens(response.json())

    def _refresh_access_token(self):
        response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.tokens["refresh_token"],
            },
        )
        response.raise_for_status()
        self._save_tokens(response.json())

    def _get_access_token(self):
        if self._is_token_expired():
            self._refresh_access_token()
        return self.tokens["access_token"]

    # ---------------------------
    # API calls
    # ---------------------------

    def get_activities(self, after_date, per_page=200):
        """
        Fetch all activities after a given datetime.
        """
        after_ts = int(after_date.replace(tzinfo=timezone.utc).timestamp())
        page = 1
        activities = []

        while True:
            resp = requests.get(
                os.path.join(STRAVA_BASE_URL, "athlete/activities"),
                headers={"Authorization": f"Bearer {self._get_access_token()}"},
                params={
                    "after": after_ts,
                    "per_page": per_page,
                    "page": page,
                },
            )
            resp.raise_for_status()
            batch = resp.json()

            if not batch:
                break

            activities.extend(batch)
            page += 1

        return activities

    def get_athlete_profile(self):
        """
        Fetch Strava athlete profile
        """
        resp = requests.get(
            os.path.join(STRAVA_BASE_URL, "athlete"), headers={"Authorization": f"Bearer {self._get_access_token()}"}
        )
        resp.raise_for_status()
        athlete = resp.json()
        return athlete
