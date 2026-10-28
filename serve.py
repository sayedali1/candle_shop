"""Local test server that tells the browser never to keep old copies, so a reload always shows the newest files."""
import http.server, socketserver, sys

class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, max-age=0')
        super().end_headers()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True
with socketserver.ThreadingTCPServer(('', port), NoCache) as httpd:   # threads: files are served in parallel, like a real host
    print(f'Serving on http://localhost:{port} (no cache)')
    httpd.serve_forever()
