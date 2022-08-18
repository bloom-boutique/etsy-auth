from __future__ import annotations
from dataclasses import dataclass
import json

from secrets import token_bytes
from hashlib import sha256
from base64 import urlsafe_b64encode
from requests import request
from urllib.parse import urlencode
from urllib.parse import quote_plus

from scope import Scope


CONNECT_URL = "https://www.etsy.com/oauth/connect"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"


def etsy_b64encode(data: str) -> bytes:
    return urlsafe_b64encode(data).rstrip(b"=")


@dataclass(frozen=True)
class Auth:
    keystring: str
    scopes: list[Scope]
    redirect: str

    def setup_auth(self) -> AuthState:
        verifier = etsy_b64encode(token_bytes(32))
        h = sha256()
        h.update(verifier)
        sha = etsy_b64encode(h.digest())

        state = etsy_b64encode(token_bytes(32))

        scopes = " ".join([s.value for s in self.scopes])

        params = urlencode({
            "response_type": "code",
            "client_id": self.keystring,
            "redirect_uri": self.redirect,
            "scope": scopes,
            "state": state,
            "code_challenge": sha,
            "code_challenge_method": "S256",
        })
        url = f"{CONNECT_URL}?{params}"
        return AuthState(url, verifier, state)

    def _token_request(self, method: str, grant: str, **kwargs: str | bytes) -> dict:
        r = request(
            method,
            TOKEN_URL,
            data={"grant_type": grant, "client_id": self.keystring} | kwargs,
        )
        response = dict(json.loads(r.content.decode("utf-8")))
        if "error" in response:
            raise ValueError(response["error"] + ": " + response["error_description"])
        else:
            return response

    def get_token(self, state: AuthState, auth_code: str) -> AuthTokens:
        data = self._token_request(
            "POST",
            "authorization_code",
            redirect_uri=self.redirect,
            code=auth_code,
            code_verifier=state.verifier,
        )
        return AuthTokens(data["access_token"], data["refresh_token"])

    def refresh_token(self, token: str) -> AuthTokens:
        data = self._token_request(
            "GET",
            "refresh_token",
            refresh_token=token,
        )
        return AuthTokens(data["access_token"], data["refresh_token"])


@dataclass(frozen=True)
class AuthState:
    auth_url: str
    verifier: bytes
    state: bytes


@dataclass(frozen=True)
class AuthTokens:
    access: str
    refresh: str
