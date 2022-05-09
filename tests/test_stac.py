import datetime
import unittest

import pytest
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import RasterExtension

from stactools.threedep import stac
from stactools.threedep.constants import USGS_FTP_BASE
from tests import test_data


class CreateItemTest(unittest.TestCase):
    def test_create_item_1(self) -> None:
        path = test_data.get_path(
            "data-files/base/1/TIFF/current/n41w106/USGS_1_n41w106.xml"
        )
        item = stac.create_item(path)
        self.assertEqual(item.id, "n41w106-1")
        self.assertTrue(item.geometry is not None)
        self.assertTrue(item.bbox is not None)
        self.assertEqual(
            item.datetime,
            datetime.datetime(2020, 10, 10, 0, 0, 0, tzinfo=datetime.timezone.utc),
        )
        self.assertEqual(
            item.common_metadata.start_datetime,
            datetime.datetime(2020, 10, 3, 0, 0, 0, tzinfo=datetime.timezone.utc),
        )
        self.assertEqual(
            item.common_metadata.end_datetime,
            datetime.datetime(2020, 10, 10, 0, 0, 0, tzinfo=datetime.timezone.utc),
        )

        data = item.assets["data"]
        self.assertEqual(
            data.href,
            (
                "https://prd-tnm.s3.amazonaws.com/StagedProducts"
                "/Elevation/1/TIFF/current/n41w106/USGS_1_n41w106.tif"
            ),
        )
        self.assertEqual(data.title, "USGS 1 Arc Second n41w106 20220331")
        self.assertIsNone(data.description)
        self.assertTrue(
            data.media_type, "image/tiff; application=geotiff; profile=cloud-optimized"
        )
        self.assertTrue(data.roles, ["data"])
        raster = RasterExtension.ext(data)
        assert raster.bands
        assert len(raster.bands) == 1
        self.assertDictEqual(
            raster.bands[0].to_dict(),
            {
                "nodata": -999999.0,
                "sampling": "point",
                "data_type": "float32",
                "spatial_resolution": 30,
            },
        )

        data = item.assets["metadata"]
        self.assertEqual(
            data.href,
            (
                "https://prd-tnm.s3.amazonaws.com/StagedProducts"
                "/Elevation/1/TIFF/current/n41w106/USGS_1_n41w106.xml"
            ),
        )
        self.assertTrue(data.title is None)
        self.assertTrue(data.description is None)
        self.assertEqual(data.media_type, "application/xml")
        self.assertEqual(data.roles, ["metadata"])

        data = item.assets["thumbnail"]
        self.assertEqual(
            data.href,
            (
                "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/"
                "1/TIFF/current/n41w106/USGS_1_n41w106.jpg"
            ),
        )
        self.assertTrue(data.title is None)
        self.assertTrue(data.description is None)
        self.assertEqual(data.media_type, "image/jpeg")
        self.assertEqual(data.roles, ["thumbnail"])

        data = item.assets["gpkg"]
        self.assertEqual(
            data.href,
            (
                "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/"
                "1/TIFF/current/n41w106/n41w106.gpkg"
            ),
        )
        self.assertTrue(data.title is None)
        self.assertEqual(
            data.description,
            "Spatially-referenced polygonal footprints of the source data used "
            "to assemble the DEM layer. The attributes of each source dataset, "
            "such as original spatial resolution, production method, and date "
            "entered into the standard DEM, are linked to these footprints.",
        )
        self.assertEqual(data.media_type, "application/geopackage+sqlite3")
        self.assertEqual(data.roles, ["metadata"])

        link = next(link for link in item.links if link.rel == "via")
        self.assertTrue(link is not None)
        self.assertEqual(
            link.target,
            (
                "https://prd-tnm.s3.amazonaws.com/StagedProducts"
                "/Elevation/1/TIFF/current/n41w106/USGS_1_n41w106.xml"
            ),
        )

        projection = ProjectionExtension.ext(item)
        self.assertEqual(projection.epsg, 4269)
        self.assertEqual(projection.shape, (3612, 3612))
        self.assertEqual(
            projection.transform,
            [
                0.00027777777803598015,
                0.0,
                -106.00166666708242,
                0.0,
                -0.000277777777786999,
                41.00166666678416,
            ],
        )

        item.validate()

    def test_create_item_1_weird_date(self) -> None:
        path = test_data.get_path("data-files/one-offs/USGS_1_n19w090.xml")
        item = stac.create_item(path)
        self.assertEqual(
            item.datetime,
            datetime.datetime(2013, 11, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
        )

    def test_create_item_13(self) -> None:
        path = test_data.get_path(
            "data-files/base/13/TIFF/current/n41w106/USGS_13_n41w106.xml"
        )
        item = stac.create_item(path)
        self.assertEqual(item.id, "n41w106-13")

    @pytest.mark.skip("FTP server doesn't resolve")
    def test_create_item_with_base(self) -> None:
        path = test_data.get_path(
            "data-files/base/1/TIFF/current/n41w106/USGS_1_n41w106.xml"
        )
        item = stac.create_item(path, base=USGS_FTP_BASE)
        data = item.assets["data"]
        self.assertEqual(
            data.href,
            (
                "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged"
                "/Elevation/1/TIFF/current/n41w106/USGS_1_n41w106.tif"
            ),
        )
        data = item.assets["metadata"]
        self.assertEqual(
            data.href,
            (
                "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged"
                "/Elevation/1/TIFF/current/n41w106/USGS_1_n41w106.xml"
            ),
        )
        data = item.assets["thumbnail"]
        self.assertEqual(
            data.href,
            (
                "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Elevation/"
                "1/TIFF/current/n41w106/USGS_1_n41w106.jpg"
            ),
        )
        link = next(link for link in item.links if link.rel == "via")
        self.assertTrue(link is not None)
        self.assertEqual(
            link.target,
            (
                "ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged"
                "/Elevation/1/TIFF/current/n41w106/USGS_1_n41w106.xml"
            ),
        )

    @pytest.mark.skip("FTP server doesn't resolve")
    def test_create_item_from_product_and_id(self) -> None:
        path = test_data.get_path("data-files/base")
        item = stac.create_item_from_product_and_id("1", "n41w106", base=path)
        item.validate()

    def test_read_href_modifier(self) -> None:
        did_it = False

        def modify_href(href: str) -> str:
            nonlocal did_it
            did_it = True
            return href

        path = test_data.get_path(
            "data-files/base/1/TIFF/current/n41w106/USGS_1_n41w106.xml"
        )
        _ = stac.create_item(path, modify_href)
        self.assertTrue(did_it)
