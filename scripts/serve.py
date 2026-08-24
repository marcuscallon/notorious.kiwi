#!/usr/bin/env python3
"""Serve the built site from src/ and open the local URL.

Usage:
  python3 scripts/serve.py          # host on port 8000, auto-open
  python3 scripts/serve.py 8080     # explicitly set a port

Behaviour:
  - Serves src/ over HTTP because src/profile.html + assets live there.
  - Auto-opens the URL in your default browser.
"""
import os, socket, threading, time, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# Serve from src/ by default
ROOT = "src"

def find_free_port(preferred=None):
    candidates = [preferred] if preferred else [8000, 8001, 8002, 3000, 5000]
    for port in candidates:
        with socket.socket() as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    raise RuntimeError("Could not find a free port")

def main():
    port = find_free_port(8000)
    os.chdir(ROOT)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    def open_browser():
        webbrowser.open(f"http://localhost:{port}/")

    server = ThreadingHTTPServer(("localhost", port), QuietHandler)
    threading.Thread(target=open_browser, daemon=True).start()

    print(f"Serving {os.getcwd()} at http://localhost:{port}/")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
