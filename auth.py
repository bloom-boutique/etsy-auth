from dataclasses import dataclass
from scope import Scope


@dataclass
class EtsyAuth:
    keystring: str
    scopes: list[Scope]

    def auth_url(self) -> str:
        ...
    
    def get_token(self, response: str) -> str:
        ...
    
    def refresh_token(self, token: str) -> str:
        ...