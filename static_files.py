import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class ServerException(Exception):
    """Custom exception for server errors."""
    pass


class RequestHandler(BaseHTTPRequestHandler):
    """
    Handles GET requests by serving static files and returning
    proper error pages.
    """

    Error_Page = """\
    <html>
    <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
    </body>
    </html>
    """

    def do_GET(self):
        try:
            full_path = os.getcwd() + self.path

            if not os.path.exists(full_path):
                raise ServerException("'{0}' not found".format(self.path))

            elif os.path.isfile(full_path):
                self.handle_file(full_path)

            else:
                raise ServerException("Unknown object '{0}'".format(self.path))

        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, "rb") as reader:
                content = reader.read()
            self.send_content(content)

        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    def send_content(self, content, status=200):
        # Convert str→bytes BEFORE sending headers
        if isinstance(content, str):
            content = content.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, status=404)

