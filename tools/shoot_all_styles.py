"""Build the site once per style, serve it, and shoot the style screenshots.

Usage: python tools/shoot_all_styles.py [out_dir]

For every style in styles/ this script:
  1. builds the site with HUGO_PARAMS_STYLE set and --panicOnWarning,
  2. starts a Hugo server on a free port,
  3. waits until it answers,
  4. runs the screenshot pass against it,
  5. stops the server.

The build output goes to a separate directory so the working public/ folder
is never left in a half-built state.
"""
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUGO = os.environ.get("HUGO_BIN", "hugo")
STYLES = ["harbor", "grove", "orchid", "graphite", "saffron"]
PUBLIC = os.path.join(ROOT, "public-preview")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def wait_for_server(port, timeout=40):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/", timeout=2
            ) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "docs/reports/screens"
    outdir = os.path.join(ROOT, outdir) if not os.path.isabs(outdir) else outdir
    os.makedirs(outdir, exist_ok=True)

    # SHOOT_STYLES narrows the run, so a single style can be re-shot while
    # iterating on it.
    only = os.environ.get("SHOOT_STYLES", "").strip()
    styles = [s.strip() for s in only.split(",") if s.strip()] or STYLES

    for style in styles:
        print(f"\n=== {style} ===")

        env = dict(os.environ)
        env["HUGO_PARAMS_STYLE"] = style
        build = subprocess.run(
            [HUGO, "--gc", "--minify", "--panicOnWarning", "-d", PUBLIC],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        if build.returncode != 0:
            print(build.stdout)
            print(build.stderr)
            raise SystemExit(f"build failed for style {style}")

        port = free_port()
        server = subprocess.Popen(
            [
                HUGO,
                "server",
                "--port",
                str(port),
                "--bind",
                "127.0.0.1",
                "--disableFastRender",
                "-d",
                PUBLIC,
            ],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            if not wait_for_server(port):
                raise SystemExit(f"server did not start for style {style}")

            shoot_env = dict(os.environ)
            shoot_env["SHOOT_BASE"] = f"http://127.0.0.1:{port}"
            # The screenshot script loops over every style, so it is called
            # with a one-style list via the STYLES env var.
            shoot_env["SHOOT_STYLES"] = style
            r = subprocess.run(
                [sys.executable, os.path.join(ROOT, "tools", "shoot_styles.py"), outdir],
                cwd=ROOT,
                env=shoot_env,
                capture_output=True,
                text=True,
            )
            print(r.stdout.strip())
            if r.returncode != 0:
                print(r.stderr.strip())
                raise SystemExit(f"screenshot pass failed for style {style}")
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()

    shutil.rmtree(PUBLIC, ignore_errors=True)
    print("\nAll styles shot.")


if __name__ == "__main__":
    main()
