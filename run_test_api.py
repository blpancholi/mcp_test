#!/usr/bin/env python3
"""
Simple HTTP API to test the Intelligence Hub with curl.
Run: python run_test_api.py
Then use the curl commands from README (Test with curl section).
"""
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

# Ensure project root is on path
sys.path.insert(0, ".")


class QueryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/health":
            self._send_json(200, {"status": "ok", "message": "Intelligence Hub test API. POST /query with {\"query\": \"...\"}"})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/query":
            self._send_json(404, {"error": "Not found. Use POST /query"})
            return
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json(400, {"error": "Body required: {\"query\": \"your question\"}"})
            return
        try:
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            query = data.get("query")
            if not query or not isinstance(query, str):
                self._send_json(400, {"error": "Body must be JSON with \"query\": \"string\""})
                return
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        try:
            from hub.orchestrator import query_intelligence_hub
            answer = query_intelligence_hub(query)
            self._send_json(200, {"query": query, "answer": answer})
        except Exception as e:
            self._send_json(500, {"error": str(e), "query": query})

    def _send_json(self, status: int, obj: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj, indent=2).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    host = "127.0.0.1"
    port = 8765
    server = HTTPServer((host, port), QueryHandler)
    print(f"Test API: http://{host}:{port}")
    print("  GET  /health  -> check server")
    print("  POST /query   -> body: {\"query\": \"your question\"}")
    print("\nExample: curl -X POST http://127.0.0.1:8765/query -H 'Content-Type: application/json' -d '{\"query\": \"What is GST?\"}'")
    print("\nCtrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
