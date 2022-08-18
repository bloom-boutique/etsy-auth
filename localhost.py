import scope
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from base64 import b64decode
import webbrowser

from auth import Auth, AuthTokens
from scope import Scope


class Handler(BaseHTTPRequestHandler):
    code: str
    state: str
    alive: bool = True

    def __init__(self):
        ...

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        self.send_response(200)

        query = parse_qs(urlparse(self.path).query)

        # Skip any extra requests, such as favicon
        if "code" not in query:
            return

        self.state = query["state"][0]

        if "error" in query:
            raise ValueError(query["error"] + ": " +
                             query["error_description"])

        self.code = query["code"][0]
        self.alive = False


def localhost_auth(keystring: str, scopes: list[Scope]) -> AuthTokens:
    auth = Auth(keystring, scopes, "http://localhost:3000")
    state = auth.setup_auth()

    webbrowser.open(state.auth_url)

    h = Handler()
    httpd = HTTPServer(("", 3000), h)
    while h.alive:
        httpd.handle_request()

    if state.state.decode("utf-8") != h.state:
        raise ValueError(
            "State value is invalid - could be corruption or CSRF")

    return auth.get_token(state, h.code)
