from __future__ import annotations
from dataclasses import dataclass
import json

from secrets import token_bytes
from hashlib import sha256
from base64 import urlsafe_b64encode
from requests import Request, post

from scope import Scope


CONNECT_URL = "https://www.etsy.com/oauth/connect"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"


@dataclass(frozen=True)
class Auth:
    keystring: str
    scopes: list[Scope]
    redirect: str

    def setup_auth(self) -> AuthState:
        verifier = token_bytes(32)
        h = sha256()
        h.update(verifier)
        sha = h.digest()

        state = token_bytes(32)

        scopes = " ".join([s.value for s in self.scopes])

        r = Request(
            method="GET",
            url=CONNECT_URL,
            data={
                "response_type": "code",
                "client_id": self.keystring,
                "redirect_uri": self.redirect,
                "scope": scopes,
                "state": urlsafe_b64encode(state),
                "code_challenge": urlsafe_b64encode(sha),
                "code_challenge_method": "S256",
            }
        )
        url = r.prepare().url
        if not url:
            raise ValueError("Malformed data to URL builder")

        return AuthState(url, verifier, state)

    def get_token(self, state: AuthState, auth_code: str) -> AuthTokens:
        r = post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": self.keystring,
                "redirect_uri": self.redirect,
                "code": auth_code,
                "code_verifier": urlsafe_b64encode(state.verifier)
            }
        )

        data = json.loads(r.content)
        if "error" in data:
            raise ValueError(data["error"])
        
        return AuthTokens(data["access_token"], data["refresh_token"])

    def refresh_token(self, token: str) -> str:
        ...


@dataclass(frozen=True)
class AuthState:
    auth_url: str
    verifier: bytes
    state: bytes


@dataclass(frozen=True)
class AuthTokens:
    access: str
    refresh: str
