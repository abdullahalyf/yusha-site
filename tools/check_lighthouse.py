"""Run Lighthouse against the mobile home page of every style.

Usage: python tools/check_lighthouse.py

For each style the site is built, served, and Lighthouse is run against the
home page with its mobile preset. The four scores are printed as a table
and the JSON reports are left in docs/reports/lighthouse/.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shoot import free_port  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUGO = os.environ.get("HUGO_BIN", "hugo")
PUBLIC = os.path.join(ROOT, "public-lighthouse")
OUTDIR = os.path.join(ROOT, "docs", "reports", "lighthouse")


def lighthouse_cmd():
    """The command that runs Lighthouse.

    The npm shim is a shell script, which Windows cannot exec directly, so
    the CLI's JavaScript entry point is run with node instead.
    """
    explicit = os.environ.get("LIGHTHOUSE_BIN")
    if explicit:
        return explicit.split()
    npm_root = os.path.join(
        os.environ.get("APPDATA", ""), "npm", "node_modules", "lighthouse"
    )
    cli = os.path.join(npm_root, "cli", "index.js")
    if os.path.exists(cli):
        return ["node", cli]
    return ["lighthouse"]

STYLES = ["harbor", "grove", "orchid", "graphite", "saffron"]
CATEGORIES = ["performance", "accessibility", "best-practices", "seo"]


def wait_for_server(port, timeout=40):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def build(style):
    env = dict(os.environ)
    env["HUGO_PARAMS_STYLE"] = style
    subprocess.run(
        [HUGO, "--gc", "--minify", "--panicOnWarning", "--destination", PUBLIC],
        cwd=ROOT, env=env, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )


def serve(port, style):
    """Serve the built site the way a real host would.

    Hugo's dev server sends nothing compressed and sets no cache headers,
    which makes every Lighthouse run report the same two false failures.
    The static server in tools/serve_static.py brotli-compresses text and
    sets a long cache lifetime for fingerprinted assets, so the numbers
    reflect what a visitor actually gets.
    """
    if not os.path.isdir(PUBLIC):
        raise RuntimeError(f"{PUBLIC} does not exist; build it first")
    proc = subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "tools", "serve_static.py"),
         PUBLIC, str(port)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not wait_for_server(port):
        proc.terminate()
        raise RuntimeError("static server did not start")
    return proc


def run_lighthouse(url, report_path):
    """Run Lighthouse with the mobile preset and return the four scores."""
    cmd = lighthouse_cmd() + [
        url,
        "--output=json",
        f"--output-path={report_path}",
        "--quiet",
        "--only-categories=performance,accessibility,best-practices,seo",
        "--chrome-flags=--headless=new --no-sandbox --disable-gpu",
    ]
    res = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    if not os.path.exists(report_path):
        print(res.stdout.decode("utf-8", "replace")[-3000:])
        raise RuntimeError(f"lighthouse produced no report for {url}")
    with open(report_path, encoding="utf-8") as fh:
        data = json.load(fh)
    scores = {}
    for cat in CATEGORIES:
        c = data.get("categories", {}).get(cat)
        scores[cat] = round((c.get("score") or 0) * 100) if c else None
    return scores, data


def failing_audits(data):
    """The audits that scored below 1, for the report."""
    out = []
    for cat in CATEGORIES:
        c = data.get("categories", {}).get(cat, {})
        for ref in c.get("auditRefs", []):
            a = data.get("audits", {}).get(ref.get("id", ""), {})
            if a.get("score") is not None and a.get("score") < 1:
                out.append((cat, ref.get("id"), a.get("title")))
    return out


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    results = {}
    for style in STYLES:
        print(f"\n=== {style} ===", flush=True)
        build(style)
        port = free_port()
        proc = serve(port, style)
        report = os.path.join(OUTDIR, f"task02-{style}-mobile.json")
        try:
            scores, data = run_lighthouse(f"http://127.0.0.1:{port}/", report)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        results[style] = scores
        print("  " + "  ".join(f"{k}: {v}" for k, v in scores.items()), flush=True)
        for cat, aid, title in failing_audits(data):
            print(f"    failing [{cat}] {aid}: {title}")

    shutil.rmtree(PUBLIC, ignore_errors=True)

    print(f"\n{'=' * 72}")
    header = f"{'style':<10}" + "".join(f"{c:>16}" for c in CATEGORIES)
    print(header)
    print("-" * len(header))
    worst = 100
    for style, scores in results.items():
        row = f"{style:<10}" + "".join(
            f"{scores[c] if scores[c] is not None else '-':>16}" for c in CATEGORIES
        )
        print(row)
        for c in CATEGORIES:
            if scores[c] is not None:
                worst = min(worst, scores[c])
    print("-" * len(header))
    print(f"lowest score across all styles and categories: {worst}")

    # The full Lighthouse JSON is several hundred kilobytes each, which is
    # too much to keep in the repository, so only the scores, the metrics
    # and the failing audits are written down.
    compact = {}
    for style, scores in results.items():
        raw = json.load(
            open(os.path.join(OUTDIR, f"task02-{style}-mobile.json"), encoding="utf-8")
        )
        a = raw.get("audits", {})
        compact[style] = {
            "scores": scores,
            "metrics": {
                k: {
                    "value": a[k].get("numericValue"),
                    "display": a[k].get("displayValue"),
                }
                for k in ["first-contentful-paint", "largest-contentful-paint",
                          "total-blocking-time", "cumulative-layout-shift",
                          "speed-index", "interactive"]
                if k in a
            },
            "failing_audits": [
                {
                    "category": cat,
                    "id": ref["id"],
                    "title": a.get(ref["id"], {}).get("title"),
                    "score": a.get(ref["id"], {}).get("score"),
                }
                for cat, c in raw.get("categories", {}).items()
                for ref in c.get("auditRefs", [])
                if a.get(ref["id"], {}).get("score") is not None
                and a[ref["id"]]["score"] < 1
            ],
        }
        os.remove(os.path.join(OUTDIR, f"task02-{style}-mobile.json"))

    with open(os.path.join(OUTDIR, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(compact, fh, indent=2)
    return 0 if worst >= 95 else 1


if __name__ == "__main__":
    sys.exit(main())
