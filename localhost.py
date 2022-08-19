from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

from .auth import Auth, AuthState, AuthTokens
from .scope import Scope


class _Handler(BaseHTTPRequestHandler):
    code: str
    state: str
    alive: bool = True

    def __init__(self):
        ...

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        self.send_response(200)

        response = code_from_http_request(self)
        if response:
            self.code, self.state = code_from_http_request(self)
            self.alive = False


def code_from_http_request(handler: BaseHTTPRequestHandler) -> tuple[str, bytes] | None:
    """
    Get the `code` and `state` queries from a HTTP request.
    If the request is not a valid Etsy API request (eg a favicon get), return `None`.
    """
    query = parse_qs(urlparse(handler.path).query)

    if "code" not in query:
        return None
    elif "error" in query:
        raise ValueError(query["error"] + ": " + query["error_description"])

    return query["code"][0], query["state"][0]


def localhost_redirect(auth: Auth, state: AuthState, port: int = 3000) -> AuthTokens:
    """
    Helper function for grabbing the Etsy access code from a localhost request.
    Suitable for local apps and testing, web-based apps should instead use a dedicated HTTPS URL.
    """
    h = _Handler()
    httpd = HTTPServer(("", port), h)
    while h.alive:
        httpd.handle_request()

    if state.state.decode("utf-8") != h.state:
        raise ValueError(
            "State value is invalid - could be corruption or CSRF attack")

    return auth.get_token(state, h.code)


def localhost_auth_workflow(keystring: str, scopes: list[Scope]) -> AuthTokens:
    """
    Authentication workflow helper function using a `localhost:3000` redirect.
    For web-based apps, it is better to redirect to a dedicated HTTPS URL.
    This will automatically open the Etsy access grant link in a web browser.
    """
    auth = Auth(keystring, scopes, "http://localhost:3000")
    state = auth.setup_auth()

    webbrowser.open(state.auth_url)

    return localhost_redirect(auth, state)