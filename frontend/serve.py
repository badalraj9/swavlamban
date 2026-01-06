import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Serve index.html for root
        if self.path == '/':
            self.path = '/frontend/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    # Ensure we are in root
    if not os.path.exists("hell_test.log"):
        print("Warning: hell_test.log not found in current directory.")

    print(f"Serving SWARM-01 UI at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
