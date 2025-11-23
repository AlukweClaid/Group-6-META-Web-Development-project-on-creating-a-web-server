class ServerException(Exception):
    pass
'''
Simple HTTP server to list directory contents and serve files.'''

import os
import sys
import subprocess
from http.server import BaseHTTPRequestHandler

class DirectoryHandler(BaseHTTPRequestHandler):

    # --- CASE HANDLERS ---
    class case_no_file(object):
        """File or directory does not exist."""

        def test(self, handler):
            return not os.path.exists(handler.full_path)

        def act(self, handler):
            raise ServerException(f"'{handler.path}' not found")


    class case_existing_file(object):
        """Existing regular file."""

        def test(self, handler):
            return os.path.isfile(handler.full_path)

        def act(self, handler):
            handler.handle_file(handler.full_path)


    class case_directory_index_file(object):
        """Directory containing index.html"""

        def index_path(self, handler):
            return os.path.join(handler.full_path, "index.html")

        def test(self, handler):
            return os.path.isdir(handler.full_path) and \
                   os.path.isfile(self.index_path(handler))

        def act(self, handler):
            handler.handle_file(self.index_path(handler))


    class case_directory_no_index_file(object):
        """Directory without index.html → show listing."""

        def test(self, handler):
            return os.path.isdir(handler.full_path)

        def act(self, handler):
            handler.handle_directory(handler.full_path)


    class case_always_fail(object):
        """Fallback case."""

        def test(self, handler):
            return True

        def act(self, handler):
            raise ServerException(f"Unknown object '{handler.path}'")


    # Order matters—directory cases go between file and fail
    Cases = [
        case_no_file,
        case_existing_file,
        case_directory_index_file,
        case_directory_no_index_file,
        case_always_fail
    ]



    # --- REQUEST HANDLING ---
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def handle_request(self):
        try:
            self.full_path = os.getcwd() + self.path

            # Check for CGI (simple: .py files)
            if self.full_path.endswith('.py') and os.path.isfile(self.full_path):
                self.run_cgi(self.full_path)
                return

            # Use case handlers
            for case in self.Cases:
                handler = case()
                if handler.test(self):
                    handler.act(self)
                    break

        except Exception as msg:
            self.handle_error(msg)

    def run_cgi(self, script_path):
        """Run a Python script as CGI."""
        try:
            # Set up environment variables for CGI
            env = os.environ.copy()
            env['REQUEST_METHOD'] = self.command
            env['PATH_INFO'] = self.path
            env['QUERY_STRING'] = self.path.split('?', 1)[1] if '?' in self.path else ''
            env['CONTENT_TYPE'] = self.headers.get('Content-Type', '')
            env['CONTENT_LENGTH'] = self.headers.get('Content-Length', '')

            # Read POST data if present
            post_data = None
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else b''

            # Run the script
            proc = subprocess.Popen(
                [sys.executable, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            stdout, stderr = proc.communicate(input=post_data)

            # Output
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(stdout)
            if stderr:
                self.wfile.write(b"<pre>" + stderr + b"</pre>")
        except Exception as e:
            self.handle_error(f"CGI error: {e}")


    # --- FILE HANDLING ---
    def handle_file(self, full_path):
        """Serve a normal file."""
        try:
            with open(full_path, "rb") as reader:
                content = reader.read()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content)

        except IOError:
            self.handle_error(f"Cannot read file: {full_path}")


    # --- DIRECTORY LISTING ---
    def handle_directory(self, full_path):
        """Generate directory listing."""
        try:
            items = os.listdir(full_path)
            items.sort()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # Start HTML
            self.wfile.write(
                bytes(f"<html><body><h1>Directory listing for {self.path}</h1>", "utf-8")
            )
            self.wfile.write(bytes("<ul>", "utf-8"))

            # List items
            for name in items:
                full_url = os.path.join(self.path, name)
                real_path = os.path.join(full_path, name)

                if os.path.isdir(real_path):
                    name += "/"
                    full_url += "/"

                self.wfile.write(
                    bytes(f"<li><a href='{full_url}'>{name}</a></li>", "utf-8")
                )

            self.wfile.write(bytes("</ul></body></html>", "utf-8"))

        except Exception as msg:
            self.handle_error(msg)


    # --- ERROR HANDLING ---
    def handle_error(self, msg):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(f"<h1>Error: {msg}</h1>", "utf-8"))

