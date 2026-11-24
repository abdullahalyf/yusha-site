"""Take the TASK-02 style screenshots with headless Chrome over CDP.

Usage: python tools/shoot_styles.py [out_dir]

One shot per style: home page, desktop (1280), light. Plus a second shot per
style: home page, mobile (375), dark. That is the 10 files the task asks for.

The style is switched by rebuilding the site with HUGO_PARAMS_STYLE set, so
the script expects the server to already be running with the style that is
currently wanted. Use --style to name the style in the file names.

The CDP client is the same one tools/shoot.py uses, because the plain
Chrome --screenshot flag cannot set prefers-color-scheme, and this script
needs the dark theme on mobile.
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

# SHOOT_STYLES narrows the run to a single style; tools/shoot_all_styles.py
# sets it so each style is shot against the server that was built for it.
_styles_env = os.environ.get("SHOOT_STYLES", "").strip()
STYLES = (
    [s.strip() for s in _styles_env.split(",") if s.strip()]
    if _styles_env
    else ["harbor", "grove", "orchid", "graphite", "saffron"]
)

# label, width, height, theme
SHOTS = [
    ("desktop-light", 1280, 900, "light"),
    ("mobile-dark", 375, 780, "dark"),
]


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
        header.append(0x81)
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
            if opcode == 0x9:
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
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/json/version", timeout=2
            ) as r:
                return json.load(r)["webSocketDebuggerUrl"]
        except Exception:
            time.sleep(0.25)
    raise TimeoutError("chrome devtools did not come up")


def shoot(cdp, session, base, style, label, w, h, theme, outdir):
    cdp.call(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": w,
            "height": h,
            "deviceScaleFactor": 1,
            "mobile": label.startswith("mobile"),
            "screenWidth": w,
            "screenHeight": h,
        },
        session,
    )
    # The media emulation has to be in place *before* the document is parsed,
    # otherwise the no-flash theme script reads the default scheme.
    cdp.call("Page.navigate", {"url": base + "/"}, session)
    time.sleep(0.5)
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
    time.sleep(2.0)

    shot = cdp.call("Page.captureScreenshot", {"format": "png"}, session)
    data = base64.b64decode(shot["data"])

    name = f"task02-{style}-{label}.png"
    out = os.path.join(outdir, name)
    with open(out, "wb") as fh:
        fh.write(data)
    return name, len(data)


def main():
    base = os.environ.get("SHOOT_BASE", "http://127.0.0.1:1313")
    outdir = sys.argv[1] if len(sys.argv) > 1 else "docs/reports/screens"
    os.makedirs(outdir, exist_ok=True)

    port = free_port()
    profile = tempfile.mkdtemp(prefix="shoot-styles-")
    proc = start_chrome(port, profile)
    try:
        ws = wait_for_devtools(port)
        cdp = Cdp(ws)
        cdp.connect()

        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call(
            "Target.attachToTarget", {"targetId": tid, "flatten": True}
        )["sessionId"]
        cdp.call("Page.enable", {}, session)

        for style in STYLES:
            for label, w, h, theme in SHOTS:
                name, size = shoot(cdp, session, base, style, label, w, h, theme, outdir)
                print(f"OK  {name} ({w}x{h} {theme}) {size} bytes")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
