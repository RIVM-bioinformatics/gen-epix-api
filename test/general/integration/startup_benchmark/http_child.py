"""Serve controllable health responses for isolated process lifecycle tests."""

import http.server
import json
import os
import subprocess
import sys
import time

port, behavior = int(sys.argv[1]), sys.argv[2]
nonce = json.loads(os.environ["TEST_API__HTTP_HEADER__GENERAL"][6:])[
    "X-Startup-Benchmark-Instance"
]
if behavior == "exit":
    sys.exit(17)
if behavior == "delay":
    time.sleep(0.2)
if behavior == "descendant":
    subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(120)",
        ]
    )


class Handler(http.server.BaseHTTPRequestHandler):
    """Serve health with configured status, nonce, or response delay."""

    count = 0

    def do_GET(self):
        """Handle one request without following redirects."""
        Handler.count += 1
        if behavior == "slow":
            time.sleep(2)
        status = (
            302
            if behavior == "redirect"
            else (
                503
                if behavior == "non200" or (behavior == "retry" and Handler.count < 3)
                else 200
            )
        )
        self.send_response(status)
        if behavior != "missing":
            self.send_header(
                "X-Startup-Benchmark-Instance",
                "stale" if behavior == "wrong" else nonce,
            )
        if status == 302:
            self.send_header("Location", "/v1/health")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"{}")


http.server.HTTPServer.allow_reuse_address = True
http.server.HTTPServer(("127.0.0.1", port), Handler).serve_forever()
