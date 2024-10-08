from typing import Any
from dataclasses import dataclass
import os
import json
import requests
from urllib.parse import urljoin
import webbrowser

from .auth import BASE, Auth, AuthTokens
from .localhost import localhost_redirect


@dataclass
class TokenStore:
    """
    Wrapper around an Etsy authentication session that will automatically load
    and store keys from `~/.etsy_keys`.
    """
    auth: Auth
    path: str = os.path.join(os.path.expanduser("~"), ".etsy_keys")

    def __post_init__(self) -> None:
        try:
            self._load_tokens()
        except FileNotFoundError:
            self._auth_workflow()

    def _dump_tokens(self) -> None:
        with open(self.path, "w") as f:
            f.write(self.tokens.access + "\n" + self.tokens.refresh)

    def _load_tokens(self) -> None:
        with open(self.path, "r") as f:
            self.tokens = AuthTokens(*f.read().split())

    def _auth_workflow(self) -> None:
        state = self.auth.setup_auth()

        webbrowser.open(state.auth_url)

        self.tokens = localhost_redirect(self.auth, state)
        self._dump_tokens()

    def _refresh(self) -> None:
        self.tokens = self.auth.refresh_token(self.tokens.refresh)
        self._dump_tokens()

    def _try_request(self, method: str, endpoint: str, params: dict[str, str]) -> dict[str, Any] | None:
        r = requests.request(
            method,
            urljoin(BASE, endpoint),
            headers={
                "x-api-key": self.auth.keystring,
                "authorization": "Bearer " + self.tokens.access
            },
            params=params,
        )
        return None if r.status_code == 401 else json.loads(r.content.decode("utf-8"))

    def _handle(self, data: dict[str, str]) -> dict[str, str]:
        if "error" in data:
            raise UserWarning(data["error"])

        return data

    def api_request(self, method: str, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Make a single request to the Etsy API.
        If an hour has elapsed since last request, refresh the tokens and try again.
        If 90 days has elapsed since last user auth, perform localhost auth workflow and try again.
        """
        r1 = self._try_request(method, endpoint, params)
        if r1 is not None:
            return self._handle(r1)

        try:
            self._refresh()
            r2 = self._try_request(method, endpoint, params)
            if r2 is not None:
                return self._handle(r2)
        except Exception as e:
            print(e)

        self._auth_workflow()
        r3 = self._try_request(method, endpoint, params)
        if r3 is not None:
            return self._handle(r3)

        raise UserWarning(
            "Unknown authentication error - is the Etsy API down?")
