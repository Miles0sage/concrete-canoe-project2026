#!/usr/bin/env python3
"""
NAU Concrete Canoe 2026 - Local Web Server
Serves the docs/ website AND proxies Ollama API requests.

Usage:
    python3 scripts/web_server.py [--port 8000]

Then open: http://localhost:8000

Features:
- Serves docs/index.html and all static files
- Proxies /api/* requests to Ollama (localhost:11434)
- CORS headers for local development
- Streaming support for AI chat
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import os
import sys
import json
import threading

PORT = int(sys.argv[sys.argv.index('--port') + 1]) if '--port' in sys.argv else 8000
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
OLLAMA_URL = "http://localhost:11434"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCRIPTS = {
    'mix_analysis': 'mix_design/mix_analysis_system.py',
    'shop_drawings': 'scripts/generate_shop_drawings.py',
    'mix_visuals': 'scripts/generate_mix_design_visuals.py',
    'calculator': 'calculations/concrete_canoe_calculator.py',
}


class CanoeHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOCS_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        # Proxy Ollama API
        if self.path.startswith('/api/'):
            self._proxy_ollama()
        elif self.path == '/run':
            self._run_script()
        else:
            self.send_error(404)

    def do_GET(self):
        # Proxy Ollama API GET requests
        if self.path.startswith('/api/'):
            self._proxy_ollama()
        else:
            super().do_GET()

    def _proxy_ollama(self):
        """Forward request to Ollama and stream response back."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None

            url = OLLAMA_URL + self.path
            req = urllib.request.Request(url, data=body, method=self.command)
            req.add_header('Content-Type', 'application/json')

            with urllib.request.urlopen(req, timeout=120) as resp:
                # Read full response and forward it
                data = resp.read()
                self.send_response(resp.status)
                self.send_header('Content-Type', resp.headers.get('Content-Type', 'application/json'))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                self.wfile.flush()

        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': f'Cannot connect to Ollama at {OLLAMA_URL}. Is it running? Start with: ollama serve'
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _run_script(self):
        """Run a Python script and return output."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))
            script_key = body.get('script', '')

            # Security: only allow known scripts
            if script_key in SCRIPTS:
                script_path = os.path.join(PROJECT_ROOT, SCRIPTS[script_key])
            elif script_key in SCRIPTS.values():
                script_path = os.path.join(PROJECT_ROOT, script_key)
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Unknown script: {script_key}'}).encode())
                return

            if not os.path.exists(script_path):
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Script not found: {script_path}'}).encode())
                return

            import subprocess
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True, text=True, timeout=300,
                cwd=PROJECT_ROOT
            )
            output = result.stdout
            if result.returncode != 0:
                output += '\n\nSTDERR:\n' + result.stderr

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'output': output, 'returncode': result.returncode}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def log_message(self, format, *args):
        """Compact logging."""
        msg = format % args
        if '/api/' in msg:
            print(f"  [AI] {msg}")
        elif '/run' in msg:
            print(f"  [SCRIPT] {msg}")
        elif '.png' in msg or '.mp4' in msg:
            pass  # Skip static asset logs
        else:
            print(f"  {msg}")


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    print("=" * 60)
    print("  NAU Concrete Canoe 2026 - Local Web Server")
    print("=" * 60)
    print(f"  Serving:  {DOCS_DIR}")
    print(f"  Ollama:   {OLLAMA_URL}")
    print(f"  Port:     {PORT}")
    print()
    print(f"  Open in browser: http://localhost:{PORT}")
    print(f"  Or from network: http://0.0.0.0:{PORT}")
    print()
    print("  Features:")
    print("    - Website with all mix design visuals")
    print("    - AI Chat (streams from Ollama on GPU)")
    print("    - Script Runner (mix analysis, shop drawings, etc.)")
    print("    - Presentation Timer with keyboard shortcuts")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    with ThreadedServer(("0.0.0.0", PORT), CanoeHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server stopped.")


if __name__ == "__main__":
    main()
