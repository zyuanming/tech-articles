"""Loopback-only teaching server; not a production service. CC0-1.0."""
import json
import platform
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from parser import parse

class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != '/':
            self.send(404,b'Not found','text/plain'); return
        self.send(200,Path(__file__).with_name('viewer.html').read_bytes(),'text/html; charset=utf-8')

    def do_POST(self):
        if self.path != '/parse':
            self.send(404,b'Not found','text/plain'); return
        try:
            length = int(self.headers.get('Content-Length','0'))
            if length < 0 or length > 4096:
                self.send(413,b'Input too large','text/plain'); return
            data = json.loads(self.rfile.read(length))
            if not isinstance(data.get('source'),str): raise ValueError('source must be string')
            r = parse(data['source']);r['python'] = platform.python_version()
            # Keep exact integers through JSON.parse in the browser.
            # Only presentation values change type; node IDs remain integers.
            if r['ok']:
                r['value'] = str(r['value'])
                r['values'] = [str(value) for value in r['values']]
            self.send(200,json.dumps(r,ensure_ascii=False).encode(),'application/json; charset=utf-8')
        except (ValueError, TypeError, AttributeError):
            self.send(400,b'Invalid request','text/plain')

if __name__ == '__main__':
    print('Teaching parser: http://127.0.0.1:8825',flush=True)
    HTTPServer(('127.0.0.1',8825),Handler).serve_forever()
