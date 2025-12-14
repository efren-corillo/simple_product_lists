from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json

items = [
    {"id": 1, "name": "Product One"},
    {"id": 2, "name": "Product Two"},
]
next_id = 3


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/items":
            self._send_json(items, 200)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/items":
            self._send_json({"error": "Not found"}, 404)
            return
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(content_length) if content_length > 0 else b""
            payload = json.loads(raw.decode("utf-8") or "{}")
            name = payload.get("name")
            if not isinstance(name, str) or not name:
                self._send_json({"error": "Invalid 'name'"}, 400)
                return
            global next_id
            item = {"id": next_id, "name": name}
            items.append(item)
            next_id += 1
            self._send_json(item, 201)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)


    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/items/"):
            id_part = path[len("/items/"):]
            try:
                item_id = int(id_part)
            except ValueError:
                self._send_json({"error": "Invalid 'id'"}, 400)
                return
            for i, it in enumerate(items):
                if it.get("id") == item_id:
                    deleted = items.pop(i)
                    self._send_json(deleted, 200)
                    return
            self._send_json({"error": "Not found"}, 404)
        else:
            self._send_json({"error": "Not found"}, 404)


def run():
    server = HTTPServer(("localhost", 3000), Handler)
    print("Server running at http://localhost:3000")
    server.serve_forever()


if __name__ == "__main__":
    run()
