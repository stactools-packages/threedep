import unittest

from stactools.threedep import utils


class PathTest(unittest.TestCase):
    def test_simple(self) -> None:
        path = utils.path("1", "n41w106")
        self.assertEqual(path, "1/TIFF/current/n41w106/USGS_1_n41w106")

    def test_extension(self) -> None:
        path = utils.path("1", "n41w106", extension="foo")
        self.assertEqual(path, "1/TIFF/current/n41w106/USGS_1_n41w106.foo")

    def test_base(self) -> None:
        path = utils.path("1", "n41w106", base="foo")
        self.assertEqual(path, "foo/1/TIFF/current/n41w106/USGS_1_n41w106")
