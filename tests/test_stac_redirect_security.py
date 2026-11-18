import unittest
from urllib.request import Request

from agrodigital.stac import STACError, _SameHostHTTPSRedirectHandler


class STACRedirectSecurityTests(unittest.TestCase):
    def setUp(self):
        self.handler = _SameHostHTTPSRedirectHandler("catalog.example:443")
        self.request = Request("https://catalog.example:443/search")

    def test_allows_https_redirect_on_same_host_and_port(self):
        redirected = self.handler.redirect_request(
            self.request, None, 302, "Found", {}, "https://catalog.example:443/next"
        )
        self.assertEqual(redirected.full_url, "https://catalog.example:443/next")

    def test_rejects_other_host_and_other_port(self):
        for target in ("https://attacker.example/next", "https://catalog.example:444/next"):
            with self.subTest(target=target), self.assertRaises(STACError):
                self.handler.redirect_request(self.request, None, 302, "Found", {}, target)

    def test_rejects_http_and_credential_urls(self):
        for target in ("http://catalog.example:443/next", "https://user:pass@catalog.example:443/next"):
            with self.subTest(target=target), self.assertRaises(STACError):
                self.handler.redirect_request(self.request, None, 302, "Found", {}, target)


if __name__ == "__main__":
    unittest.main()
