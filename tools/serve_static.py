"""A tiny static server that behaves like a real host.

Hugo's own dev server does not compress responses and does not set cache
headers, so a Lighthouse run against it always reports "enable text
compression" and "use an efficient cache policy". This server serves a
built site the way Vercel does: brotli for text, a long cache lifetime for
fingerprinted assets and no cache for the HTML.

Usage: python tools/serve_static.py <directory> <port>
"""
import argparse
import hashlib
import mimetypes
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

try:
    import brotli
except ImportError:
    brotli = None

import gzip

# Fingerprinted assets can be cached forever; the HTML never can.
IMMUTABLE_SUFFIXES = (".css", ".js", ".woff2", ".woff", ".png", ".jpg",
                       ".jpeg", ".webp", ".svg", ".avif", ".ico")


class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def end_headers(self):
        path = self.path.split("?", 1)[0]
        if path.endswith("/"):
            path += "index.html"
        if path.endswith(IMMUTABLE_SUFFIXES):
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        else:
            self.send_header("Cache-Control", "public, max-age=0, must-revalidate")
        self.send_header("Vary", "Accept-Encoding")
        super().end_headers()

    def guess_type(self, path):
        ctype, _ = mimetypes.guess_type(path)
        if path.endswith(".webp"):
            ctype = "image/webp"
        elif path.endswith(".woff2"):
            ctype = "font/woff2"
        elif path.endswith(".avif"):
            ctype = "image/avif"
        return ctype or "application/octet-stream"

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        full = os.path.join(self.directory, path.lstrip("/"))
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        if not os.path.exists(full):
            self.send_error(404)
            return

        ctype = self.guess_type(full)
        is_text = (
            ctype.startswith("text/")
            or ctype in ("application/javascript", "application/json",
                         "image/svg+xml", "application/xml")
            or full.endswith((".css", ".js", ".svg", ".html", ".xml", ".txt"))
        )
        with open(full, "rb") as fh:
            body = fh.read()

        accept = self.headers.get("Accept-Encoding", "")
        encoding = None
        if is_text and body:
            # The compression has to happen before any header is sent: an
            # exception halfway through leaves the connection half open and
            # Chrome shows an interstitial instead of the page.
            if "br" in accept and brotli is not None:
                body = brotli.compress(body, quality=5)
                encoding = "br"
            elif "gzip" in accept:
                body = gzip.compress(body, 6)
                encoding = "gzip"

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        if encoding:
            self.send_header("Content-Encoding", encoding)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        if os.environ.get("SERVE_STATIC_VERBOSE"):
            print(fmt % args, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("port", type=int)
    args = ap.parse_args()
    os.chdir(args.directory)
    # Lighthouse opens many connections at once, so the server has to handle
    # requests in threads; a single-threaded server deadlocks and Chrome
    # shows an interstitial error instead of the page.
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.daemon_threads = True
    print(f"serving {args.directory} on http://127.0.0.1:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
