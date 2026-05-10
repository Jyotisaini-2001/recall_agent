#!/usr/bin/env python3
"""
SkillForge Web Dashboard Server
Run: python3 server.py
Then open: http://localhost:8765
"""
import json
import os
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler

STATS_FILE  = os.path.join(os.path.dirname(__file__), "stats.json")
SKILLS_DIR  = os.path.join(os.path.dirname(__file__), "skills")


def _parse_skills():
    """Read all skill .md files and return a list of dicts."""
    skills = []
    if not os.path.isdir(SKILLS_DIR):
        return skills
    for fname in sorted(os.listdir(SKILLS_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(SKILLS_DIR, fname)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue
        # Parse YAML-like frontmatter between --- ... ---
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue
        fm = {}
        for line in fm_match.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
        # Parse keywords list
        kw_raw = fm.get("keywords", "[]")
        keywords = [s.strip().strip("'\"") for s in kw_raw.strip("[]").split(",") if s.strip()]
        skills.append({
            "name":        fm.get("name", fname.replace(".md", "")),
            "description": fm.get("description", ""),
            "confidence":  float(fm.get("confidence", 0.8)),
            "times_used":  int(fm.get("times_used", 0)),
            "created_at":  fm.get("created_at", ""),
            "keywords":    keywords[:4],  # first 4 keywords for display
        })
    return skills


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silence default access logs

    def do_GET(self):
        if self.path == "/api/stats":
            self._serve_stats()
        elif self.path == "/" or self.path == "/index.html":
            self._serve_file("dashboard.html", "text/html")
        else:
            super().do_GET()

    def _serve_stats(self):
        try:
            with open(STATS_FILE, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {
                "errors_processed": 0, "fast_count": 0, "slow_count": 0,
                "tokens_spent": 0, "tokens_saved": 0, "skills_in_library": 0, "log": []
            }
        # Always merge live skills from disk
        data["skills_list"] = _parse_skills()
        data["skills_in_library"] = len(data["skills_list"])
        payload = json.dumps(data)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload.encode())

    def _serve_file(self, filename, content_type):
        filepath = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)



class _ReuseServer(HTTPServer):
    allow_reuse_address = True  # prevents "Address already in use" on restart


if __name__ == "__main__":
    port = 8765
    print(f"\n🚀 SkillForge Dashboard → http://localhost:{port}\n")
    try:
        _ReuseServer(("", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
