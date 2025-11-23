from http.server import HTTPServer
from directories import DirectoryHandler

if __name__ == "__main__":
    server_address = ('', 8000)  # Listen on all interfaces, port 8000
    httpd = HTTPServer(server_address, DirectoryHandler)
    print(f"Serving HTTP on port {server_address[1]}...")
    httpd.serve_forever()
