import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agrodigital.download import DownloadError, download_asset


class FakeResponse:
    def __init__(self, data, url="https://example.test/asset.tif"):
        self.data = data
        self.offset = 0
        self.headers = {"Content-Length": str(len(data))}
        self.url = url
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def geturl(self): return self.url
    def read(self, size=-1):
        if size < 0: size = len(self.data)
        chunk = self.data[self.offset:self.offset + size]
        self.offset += len(chunk)
        return chunk


class DownloadTests(unittest.TestCase):
    @patch("agrodigital.download.build_opener")
    def test_download_and_checksum(self, opener_factory):
        payload = b"public raster bytes"
        opener_factory.return_value.open.return_value = FakeResponse(payload)
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "asset.tif"
            result = download_asset("https://example.test/asset.tif", target,
                                    sha256=hashlib.sha256(payload).hexdigest())
            self.assertEqual(target.read_bytes(), payload)
            self.assertTrue(result["verified_checksum"])
            self.assertFalse(target.with_name("asset.tif.part").exists())

    @patch("agrodigital.download.build_opener")
    def test_size_limit_removes_partial_file(self, opener_factory):
        opener_factory.return_value.open.return_value = FakeResponse(b"too large")
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "asset.tif"
            with self.assertRaises(DownloadError):
                download_asset("https://example.test/asset.tif", target, max_bytes=3)
            self.assertFalse(target.exists())
            self.assertFalse(target.with_name("asset.tif.part").exists())

    def test_rejects_non_https(self):
        with self.assertRaises(ValueError):
            download_asset("http://example.test/file", "unused.tif")


if __name__ == "__main__": unittest.main()
