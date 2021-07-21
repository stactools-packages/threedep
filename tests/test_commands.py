import os.path
from tempfile import TemporaryDirectory

import pystac
from pystac.extensions.item_assets import ItemAssetsExtension

from stactools.threedep.commands import create_threedep_command
from stactools.testing import CliTestCase

from tests import test_data


class CreateCollectionTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_threedep_command]

    def test_create_collection(self):
        path = test_data.get_path("data-files/base")
        with TemporaryDirectory() as directory:
            result = self.run_command([
                "threedep", "create-catalog", directory, "--id", "n41w106",
                "--id", "n40w106", "--quiet", "--source", path
            ])
            self.assertEqual(result.exit_code,
                             0,
                             msg="\n{}".format(result.output))
            catalog = pystac.read_file(os.path.join(directory, "catalog.json"))
            item_ids = set([item.id for item in catalog.get_all_items()])
            self.assertEqual(
                item_ids,
                set(["n40w106-1", "n40w106-13", "n41w106-1", "n41w106-13"]))

            for child in catalog.get_children():
                item_assets = ItemAssetsExtension.ext(child).item_assets

                data = item_assets["data"]
                assert data
                self.assertIsNone(data.title)
                self.assertIsNone(data.description)
                self.assertEqual(data.media_type, pystac.MediaType.COG)
                self.assertListEqual(data.roles, ["data"])

                metadata = item_assets["metadata"]
                assert metadata
                self.assertIsNone(metadata.title)
                self.assertIsNone(metadata.description)
                self.assertEqual(metadata.media_type, pystac.MediaType.XML)
                self.assertListEqual(metadata.roles, ["metadata"])

                thumbnail = item_assets["thumbnail"]
                assert thumbnail
                self.assertIsNone(thumbnail.title)
                self.assertIsNone(thumbnail.description)
                self.assertEqual(thumbnail.media_type, pystac.MediaType.JPEG)
                self.assertListEqual(thumbnail.roles, ["thumbnail"])

                gpkg = item_assets["gpkg"]
                assert gpkg
                self.assertIsNone(gpkg.title)
                self.assertIsNone(gpkg.description)
                self.assertEqual(gpkg.media_type, pystac.MediaType.GEOPACKAGE)
                self.assertListEqual(gpkg.roles, ["metadata"])
