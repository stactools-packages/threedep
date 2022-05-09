import os.path
from tempfile import TemporaryDirectory
from typing import Callable, List

import pystac
from click import Command, Group
from pystac import Catalog, Collection
from pystac.extensions.item_assets import ItemAssetsExtension
from stactools.testing.cli_test import CliTestCase

from stactools.threedep.commands import create_threedep_command


class CreateCollectionTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_threedep_command]

    def test_create_collection(self) -> None:
        with TemporaryDirectory() as directory:
            result = self.run_command(
                f"threedep create-catalog {directory} --asset-id n41w106 "
                f"--asset-id n40w106 --quiet"
            )
            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))
            catalog = pystac.read_file(os.path.join(directory, "catalog.json"))
            assert isinstance(catalog, Catalog)
            item_ids = set([item.id for item in catalog.get_all_items()])
            self.assertEqual(
                item_ids, set(["n40w106-1", "n40w106-13", "n41w106-1", "n41w106-13"])
            )

            for child in catalog.get_children():
                assert isinstance(child, Collection)
                item_assets = ItemAssetsExtension.ext(child).item_assets

                data = item_assets["data"]
                self.assertIsNone(data.title)
                self.assertIsNone(data.description)
                self.assertEqual(data.media_type, pystac.MediaType.COG)
                assert data.roles
                self.assertListEqual(data.roles, ["data"])

                metadata = item_assets["metadata"]
                self.assertIsNone(metadata.title)
                self.assertIsNone(metadata.description)
                self.assertEqual(metadata.media_type, pystac.MediaType.XML)
                assert metadata.roles
                self.assertListEqual(metadata.roles, ["metadata"])

                thumbnail = item_assets["thumbnail"]
                self.assertIsNone(thumbnail.title)
                self.assertIsNone(thumbnail.description)
                self.assertEqual(thumbnail.media_type, pystac.MediaType.JPEG)
                assert thumbnail.roles
                self.assertListEqual(thumbnail.roles, ["thumbnail"])

                gpkg = item_assets["gpkg"]
                self.assertIsNone(gpkg.title)
                self.assertIsNone(gpkg.description)
                self.assertEqual(gpkg.media_type, pystac.MediaType.GEOPACKAGE)
                assert gpkg.roles
                self.assertListEqual(gpkg.roles, ["metadata"])
