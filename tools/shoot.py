"""Take the TASK-01 screenshots with headless Chrome over CDP.

Usage: python tools/shoot.py <base_url> <out_dir>

Drives Chrome through the DevTools protocol so the viewport width, device
pixel ratio, colour scheme and scrollbar are all under our control (the
plain `--screenshot` CLI flag cannot set prefers-color-scheme).

Writes task01-<page>-<device>-<theme>.png for every page of the site, at
mobile (375) and desktop (1280), in light and dark. Blog posts are captured
full-page so the whole post is visible in one file.
"""
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# page slug, path
PAGES = [
    ("home", "/"),
    ("about", "/about/"),
    ("projects", "/projects/"),
    ("blog", "/blog/"),
    ("post-laravel", "/blog/learning-laravel-app/"),
    ("post-study", "/blog/semester-study-system/"),
    ("post-trip", "/blog/trip-to-sajek-valley/"),
    ("contact", "/contact/"),
]

# device label, width, height
DEVICES = [
    ("mobile", 375, 780),
    ("tablet", 768, 1024),
    ("desktop", 1280, 900),
]

THEMES = ["light", "dark"]

# Every page, mobile + desktop, light + dark. The trailing flag says whether
# the shot captures the whole scrollable page instead of just the viewport.
WANTED = []
for _slug, _path in PAGES:
    for _device, _w, _h in [("mobile", 375, 780), ("desktop", 1280, 900)]:
        for _theme in THEMES:
            _full = _slug.startswith("post-")
            WANTED.append((_slug, _path, _device, _w, _h, _theme, _full))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class Cdp:
    """Minimal Chrome DevTools Protocol client over a websocket."""

    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.sock = None
        self.next_id = 0

    def connect(self):
        import struct

        # Chrome's websocket endpoint is a ws:// URL; talk the raw protocol
        # rather than pulling in a dependency.
        assert self.ws_url.startswith("ws://")
        rest = self.ws_url[len("ws://"):]
        hostport, _, path = rest.partition("/")
        host, _, port = hostport.partition(":")
        self.sock = socket.create_connection((host, int(port)), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET /{path} HTTP/1.1\r\n"
            f"Host: {hostport}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        assert b"101" in buf.split(b"\r\n")[0], buf[:200]
        self.buf = buf.split(b"\r\n\r\n", 1)[1]

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise EOFError("websocket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, method, params=None, session=None):
        self.next_id += 1
        msg = {"id": self.next_id, "method": method, "params": params or {}}
        if session:
            msg["sessionId"] = session
        payload = json.dumps(msg).encode()
        header = bytearray()
        header.append(0x81)  # FIN + text
        mask = os.urandom(4)
        n = len(payload)
        if n < 126:
            header.append(0x80 | n)
        elif n < 65536:
            header.append(0x80 | 126)
            header += n.to_bytes(2, "big")
        else:
            header.append(0x80 | 127)
            header += n.to_bytes(8, "big")
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)
        return self.next_id

    def recv(self):
        while True:
            b0, b1 = self._read(2)
            opcode = b0 & 0x0F
            length = b1 & 0x7F
            if length == 126:
                length = int.from_bytes(self._read(2), "big")
            elif length == 127:
                length = int.from_bytes(self._read(8), "big")
            data = self._read(length)
            if opcode == 0x8:
                raise EOFError("websocket closed by peer")
            if opcode == 0x9:  # ping
                continue
            if opcode in (0x1, 0x2):
                return json.loads(data)

    def call(self, method, params=None, session=None, timeout=60):
        msg_id = self.send(method, params, session)
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.sock.settimeout(max(1, deadline - time.time()))
            msg = self.recv()
            if msg.get("id") == msg_id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
        raise TimeoutError(method)


def start_chrome(port, profile):
    args = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--disable-background-networking",
        f"--user-data-dir={profile}",
        f"--remote-debugging-port={port}",
        "about:blank",
    ]
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def wait_for_devtools(port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2) as r:
                return json.load(r)["webSocketDebuggerUrl"]
        except Exception:
            time.sleep(0.25)
    raise TimeoutError("chrome devtools did not come up")


def shoot(cdp, session, base, slug, path, device, w, h, theme, outdir, full=False):
    cdp.call(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": w,
            "height": h,
            "deviceScaleFactor": 1,
            "mobile": device == "mobile",
            "screenWidth": w,
            "screenHeight": h,
        },
        session,
    )
    # The media emulation has to be in place *before* the document is parsed,
    # otherwise the page's no-flash theme script reads the default scheme.
    # Navigating once, then setting the media and reloading, is the reliable
    # way to get there: a navigation resets the emulation.
    cdp.call("Page.navigate", {"url": base + path}, session)
    time.sleep(0.5)
    # The site remembers an explicit theme choice in localStorage, so the
    # stored value has to go or every shot after the first one reuses it.
    cdp.call(
        "Runtime.evaluate",
        {"expression": "try{localStorage.clear()}catch(e){}"},
        session,
    )
    cdp.call(
        "Emulation.setEmulatedMedia",
        {"features": [{"name": "prefers-color-scheme", "value": theme}]},
        session,
    )
    cdp.call("Page.reload", {"ignoreCache": True}, session)
    # Give the fonts and the no-flash theme script time to settle.
    time.sleep(2.0)

    if full:
        # captureBeyondViewport does not scroll, so lazy images below the fold
        # never start loading and the shot shows empty boxes. Walk down the
        # page to trigger them, then return to the top.
        cdp.call(
            "Runtime.evaluate",
            {
                "expression": (
                    "(async()=>{"
                    "const step=window.innerHeight;"
                    "for(let y=0;y<document.body.scrollHeight;y+=step){"
                    "window.scrollTo(0,y);await new Promise(r=>setTimeout(r,120));"
                    "}"
                    "window.scrollTo(0,0);"
                    "await new Promise(r=>setTimeout(r,600));"
                    "})()"
                ),
                "awaitPromise": True,
            },
            session,
        )
        time.sleep(1.0)

    shot = cdp.call(
        "Page.captureScreenshot",
        {"format": "png", "captureBeyondViewport": full},
        session,
    )
    data = base64.b64decode(shot["data"])

    name = f"task01-{slug}-{device}-{theme}.png"
    out = os.path.join(outdir, name)
    with open(out, "wb") as fh:
        fh.write(data)

    return name, out, len(data)


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:1313"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "docs/reports/screens"
    # Optional third argument: a comma-separated list of page slugs to shoot.
    # With no list, every page in PAGES is captured.
    only = [s.strip() for s in sys.argv[3].split(",") if s.strip()] if len(sys.argv) > 3 else []
    wanted = [w for w in WANTED if not only or w[0] in only]
    os.makedirs(outdir, exist_ok=True)

    port = free_port()
    profile = tempfile.mkdtemp(prefix="shoot-profile-")
    proc = start_chrome(port, profile)
    try:
        ws = wait_for_devtools(port)
        cdp = Cdp(ws)
        cdp.connect()

        # One tab for every shot: the media emulation only sticks on a
        # session that stays alive across navigations.
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        cdp.call("Page.enable", {}, session)

        for slug, path, device, w, h, theme, full in wanted:
            name, out, size = shoot(
                cdp, session, base, slug, path, device, w, h, theme, outdir, full
            )
            print(f"OK  {name} ({w}x{h} {theme}{' full' if full else ''}) {size} bytes")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
