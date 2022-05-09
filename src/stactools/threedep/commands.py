import os.path
from collections import defaultdict
from typing import List

import click
from click import Command, Group
from pystac import Catalog, CatalogType, Collection, Extent, MediaType
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from stactools.core.io import read_text

from stactools.threedep import stac, utils
from stactools.threedep.constants import (
    DESCRIPTION,
    PRODUCTS,
    USGS_3DEP_ID,
    USGS_FTP_BASE,
    USGS_PROVIDER,
)


def create_threedep_command(cli: Group) -> Command:
    """Creates the threedep command line utility."""

    @cli.group("threedep", short_help="Work with USGS 3DEP elevation data.")
    def threedep() -> None:
        pass

    @threedep.command(
        "create-catalog", short_help="Create a STAC catalog for existing USGS 3DEP data"
    )
    @click.argument("destination")
    @click.option(
        "-s",
        "--source",
        help="The href of a directory tree containing metadata",
        default=None,
    )
    @click.option(
        "-i",
        "--asset-id",
        "asset_ids",
        multiple=True,
        help="Asset ids to fetch. If not provided, will fetch all IDs.",
    )
    @click.option("--quiet/--no-quiet", default=False)
    def create_catalog_command(
        destination: str, source: str, asset_ids: List[str], quiet: bool
    ) -> None:
        """Creates a relative published 3DEP catalog in DESTINATION.

        If SOURCE is not provided, will use the metadata in AWS. SOURCE is
        expected to be a directory tree mirroring the structure on USGS, so
        it is best created using `stac threedep download-metadata`.
        """
        collections = {}
        items = defaultdict(list)
        for product in PRODUCTS:
            if not asset_ids:
                asset_ids = utils.fetch_ids(product)
            for asset_id in asset_ids:
                item = stac.create_item_from_product_and_id(
                    product, asset_id, base=source
                )
                items[product].append(item)
                if not quiet:
                    print(item.id)
            extent = Extent.from_items(items[product])
            if product == "1":
                title = "1 arc-second"
                description = "USGS 3DEP 1 arc-second DEMs"
            elif product == "13":
                title = "1/3 arc-second"
                description = "USGS 3DEP 1/3 arc-second DEMs"
            else:
                raise NotImplementedError
            collection = Collection(
                id=f"{USGS_3DEP_ID}-{product}",
                title=title,
                keywords=["USGS", "3DEP", "NED", "DEM", "elevation"],
                providers=[USGS_PROVIDER],
                description=description,
                extent=extent,
                license="PDDL-1.0",
            )
            item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
            item_assets.item_assets = {
                "data": AssetDefinition(
                    {
                        "type": MediaType.COG,
                        "roles": ["data"],
                    }
                ),
                "metadata": AssetDefinition(
                    {"type": MediaType.XML, "roles": ["metadata"]}
                ),
                "thumbnail": AssetDefinition(
                    {"type": MediaType.JPEG, "roles": ["thumbnail"]}
                ),
                "gpkg": AssetDefinition(
                    {"type": MediaType.GEOPACKAGE, "roles": ["metadata"]}
                ),
            }
            collections[product] = collection
        catalog = Catalog(
            id=USGS_3DEP_ID,
            description=DESCRIPTION,
            title="USGS 3DEP DEMs",
            catalog_type=CatalogType.RELATIVE_PUBLISHED,
        )
        for product, collection in collections.items():
            catalog.add_child(collection)
            collection.add_items(items[product])
        catalog.generate_subcatalogs("${threedep:region}")
        catalog.normalize_hrefs(destination)
        catalog.save()
        catalog.validate()

    @threedep.command(
        "download-metadata", short_help="Download all metadata for USGS 3DEP data"
    )
    @click.argument("destination")
    @click.option(
        "-i",
        "--asset-id",
        "asset_ids",
        multiple=True,
        help="Asset ids to fetch. If not provided, will fetch all IDs.",
    )
    @click.option("--quiet/--no-quiet", default=False)
    def download_metadata_command(
        destination: str, asset_ids: List[str], quiet: bool
    ) -> None:
        """Creates a 3DEP collection in DESTINATION."""
        for product in PRODUCTS:
            if not asset_ids:
                asset_ids = utils.fetch_ids(product)
            for id in asset_ids:
                path = utils.path(product, id, extension="xml", base=destination)
                if os.path.exists(path):
                    if not quiet:
                        print("{} exists, skipping download...".format(path))
                    continue
                os.makedirs(os.path.dirname(path), exist_ok=True)
                source_path = utils.path(
                    product, id, extension="xml", base=USGS_FTP_BASE
                )
                if not quiet:
                    print("{} -> {}".format(source_path, path))
                text = read_text(source_path)
                with open(path, "w") as f:
                    f.write(text)

    @threedep.command(
        "fetch-ids", short_help="Fetch all product ids and print them to stdout"
    )
    @click.argument("product")
    @click.option(
        "--usgs-ftp/--no-usgs-ftp",
        default=False,
        help="Fetch from the USGS FTP instead of AWS.",
    )
    def fetch_ids_command(product: str, usgs_ftp: bool) -> None:
        """Fetches product ids and prints them to stdout."""
        for id in utils.fetch_ids(product, use_usgs_ftp=usgs_ftp):
            print(id)

    return threedep
