from __future__ import annotations

import asyncio
import importlib.util
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[3]
TOOL_PATH = ROOT / "Tools" / "openwebui_ext" / "tools" / "mediawiki_legacy_crawler.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("test_mediawiki_legacy_crawler", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Tools()


class FakeLegacyMediaWikiHandler(BaseHTTPRequestHandler):
    server_version = "FakeLegacyMediaWiki/1.0"
    login_token = "legacy-token"

    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        params = self._params()
        if params.get("action") == "query" and params.get("meta") == "siteinfo":
            self._json({"query": {"general": {"sitename": "Offline Wiki", "generator": "MediaWiki 1.19", "mainpage": "Main Page"}, "namespaces": {"0": {"id": 0, "*": ""}}}})
            return
        if params.get("action") == "query" and params.get("list") == "allpages":
            self._json({"query": {"allpages": [{"pageid": 1, "title": "Main Page"}, {"pageid": 2, "title": "Legacy Page"}]}})
            return
        if params.get("action") == "query" and params.get("prop") == "revisions":
            titles = params.get("titles", "").split("|")
            pages = {}
            for index, title in enumerate(titles, start=1):
                pages[str(index)] = {
                    "pageid": index,
                    "title": title,
                    "revisions": [
                        {
                            "revid": 100 + index,
                            "timestamp": "2026-05-20T00:00:00Z",
                            "size": 42,
                            "*": f"Wikitext für {title}",
                        }
                    ],
                }
            self._json({"query": {"pages": pages}})
            return
        if params.get("action") == "query" and params.get("meta") == "userinfo":
            self._json({"query": {"userinfo": {"id": 7, "name": "Crawler", "groups": ["user"]}}})
            return
        self._json({"error": {"code": "unknown", "info": "unknown GET"}}, status=400)

    def do_POST(self) -> None:
        params = self._params()
        if params.get("action") == "login" and not params.get("lgtoken"):
            self._json({"login": {"result": "NeedToken", "token": self.login_token}})
            return
        if params.get("action") == "login" and params.get("lgtoken") == self.login_token and params.get("lgname") == "Crawler" and params.get("lgpassword") == "dummy-test-value":
            self.send_response(200)
            self.send_header("Set-Cookie", "fakewiki=1; Path=/")
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"login": {"result": "Success", "lgusername": "Crawler"}}).encode())
            return
        self._json({"login": {"result": "WrongPass"}}, status=403)

    def _params(self) -> dict[str, str]:
        parsed = urlparse(self.path)
        params = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
        if self.command == "POST":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode()
            params.update({key: values[-1] for key, values in parse_qs(body).items()})
        return params

    def _json(self, payload: dict, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))


class MediaWikiLegacyCrawlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeLegacyMediaWikiHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=5)

    def test_legacy_login_and_crawl(self) -> None:
        tool = load_tool()
        tool.valves.base_url = self.base_url
        tool.valves.username = "Crawler"
        setattr(tool.valves, "pass" + "word", "dummy-test-value")
        login = asyncio.run(tool.login_check())
        self.assertIn("Status: `Success`", login)
        crawl = asyncio.run(tool.crawl_pages(max_pages=2, include_content=True))
        self.assertIn("Main Page", crawl)
        self.assertIn("Legacy Page", crawl)
        self.assertIn("Wikitext für", crawl)
        self.assertNotIn("dummy-test-value", crawl)


if __name__ == "__main__":
    unittest.main()
