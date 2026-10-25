"""Local teaching UI; Python standard library only. CC0-1.0."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
from evaluator import run, LispError

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/':
            self.send_error(404)
            return
        data = Path(__file__).with_name('index.html').read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != '/eval':
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        if length > 10000:
            self.send_error(413)
            return
        try:
            source = json.loads(self.rfile.read(length))['source']
            value, machine = run(source, limit=500)
            from evaluator import show
            payload = dict(result=show(value), steps=machine.steps,
                           bindings=[e for e in machine.events if e['kind']=='bind'])
        except (LispError, RecursionError, ValueError, KeyError) as error:
            payload = dict(error=str(error))
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(data)

if __name__ == '__main__':
    HTTPServer(('127.0.0.1', 8121), Handler).serve_forever()
