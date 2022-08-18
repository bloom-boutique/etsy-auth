from __future__ import annotations
from dataclasses import dataclass

from secrets import token_bytes
from hashlib import sha256
from base64 import urlsafe_b64encode
from requests import Request

from scope import Scope


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
            url="https://www.etsy.com/oauth/connect",
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

    def get_token(self, response: str) -> str:
        ...

    def refresh_token(self, token: str) -> str:
        ...


@dataclass(frozen=True)
class AuthState:
    auth_url: str
    verifier: bytes
    state: bytes
