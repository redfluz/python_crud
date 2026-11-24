from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape

from models.user_model import UserInput
from routes.user_routes import resolve

TEMPLATE_DIRECTORY = Path(__file__).resolve().parents[1] / "templates"
TEMPLATES = Environment(
    loader=FileSystemLoader(TEMPLATE_DIRECTORY),
    autoescape=select_autoescape(["html"]),
)


def create_handler(user_service):

    class UserHandler(BaseHTTPRequestHandler):

        def do_GET(self):
            self.dispatch("GET")

        def do_POST(self):
            self.dispatch("POST")

        def dispatch(self, method):
            path = urlparse(self.path).path
            handler, arguments = resolve(method, path)

            if handler is None:
                self.respond(404, "Page not found.")
                return

            try:
                getattr(self, handler)(*arguments)
            except Exception as error:
                self.log_error("Request failed: %s", error)
                self.respond(500, "Internal server error.")

        # ------------------------------------------------------------------
        # Views
        # ------------------------------------------------------------------

        def index(self):
            self.render(
                "index.html",
                {"error": "", "users": user_service.find_all()},
            )

        def new(self):
            self.render_form()

        def edit(self, user_id):
            user = user_service.find_by_id(int(user_id))
            if user is None:
                self.respond(404, "User not found.")
                return
            self.render_form(user=user)

        # ------------------------------------------------------------------
        # Mutations
        # ------------------------------------------------------------------

        def create(self):
            data = self.form_data()
            user_input = UserInput(
                name=data.get("name", ""),
                age=data.get("age", ""),
            )
            try:
                user_service.create(user_input)
                self.redirect("/")
            except ValueError as error:
                self.render_form(
                    name=user_input.name,
                    age=user_input.age,
                    error=str(error),
                )

        def update(self, user_id):
            user_id = int(user_id)
            data = self.form_data()
            user_input = UserInput(
                name=data.get("name", ""),
                age=data.get("age", ""),
            )
            try:
                if not user_service.update(user_id, user_input):
                    self.respond(404, "User not found.")
                    return
                self.redirect("/")
            except ValueError as error:
                user = user_service.find_by_id(user_id)
                if user is None:
                    self.respond(404, "User not found.")
                    return
                self.render_form(
                    user=user,
                    name=user_input.name,
                    age=user_input.age,
                    error=str(error),
                )

        def delete(self, user_id):
            if not user_service.delete(int(user_id)):
                self.respond(404, "User not found.")
                return
            self.redirect("/")

        # ------------------------------------------------------------------
        # Rendering helpers
        # ------------------------------------------------------------------

        def render_form(self, user=None, name=None, age=None, error=""):
            is_edit = user is not None

            if name is None:
                name = user.name if is_edit else ""
            if age is None:
                age = user.age if is_edit else ""

            self.render(
                "form.html",
                {
                    "form_title": "Edit User" if is_edit else "New User",
                    "user_heading": (
                        f"Edit User #{user.id}" if is_edit else "New User"
                    ),
                    "form_action": (
                        f"/users/{user.id}/update" if is_edit else "/users"
                    ),
                    "name": name,
                    "age": age,
                    "submit_class": "btn-primary" if is_edit else "btn-success",
                    "submit_label": "Update" if is_edit else "Create",
                    "error": error,
                },
            )

        def form_data(self):
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length < 0 or content_length > 65536:
                raise ValueError("Invalid request body size.")
            body = self.rfile.read(content_length).decode("utf-8")
            data = parse_qs(body, keep_blank_values=True)
            return {key: values[0] for key, values in data.items()}

        def render(self, filename, values):
            body = TEMPLATES.get_template(filename).render(values).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def redirect(self, location):
            self.send_response(303)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def respond(self, status, message):
            body = TEMPLATES.get_template("error.html").render(
                status=status,
                message=message,
            ).encode("utf-8")

            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return UserHandler